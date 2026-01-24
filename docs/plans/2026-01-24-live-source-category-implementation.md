# Live Source Category Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add category support to live sources so recorded videos automatically inherit the source's category.

**Architecture:** Add optional `category_id` foreign key to LiveSource model, auto-create "未分类" default category on startup, modify recorder service to inherit category when creating VideoFile, add bulk category assignment endpoint, and update frontend with category dropdown and bulk assignment UI.

**Tech Stack:** FastAPI, SQLAlchemy (async), Vue 3, Element Plus, TypeScript

---

## Task 1: Add category_id to LiveSource Model

**Files:**
- Modify: `backend/app/models/source.py:11-27`

**Step 1: Add category_id field and relationship to LiveSource**

In `backend/app/models/source.py`, add after line 18 (after `url` field):

```python
category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
```

Add after line 26 (after `schedules` relationship):

```python
category = relationship("Category", back_populates="sources")
```

**Step 2: Add sources relationship to Category model**

Modify: `backend/app/models/category.py:20`

Add after line 20 (after `videos` relationship):

```python
sources = relationship("LiveSource", back_populates="category")
```

**Step 3: Verify database migration**

Run: `cd backend && python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"`

Expected: No errors, tables created/updated successfully

**Step 4: Commit**

```bash
git add backend/app/models/source.py backend/app/models/category.py
git commit -m "$(cat <<'EOF'
feat: add category_id field to LiveSource model

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Auto-create Default Category on Startup

**Files:**
- Modify: `backend/app/database.py:16-19`

**Step 1: Add function to create default category**

In `backend/app/database.py`, add after line 18 (after `init_db` function):

```python
async def ensure_default_category():
    """Ensure the default '未分类' category exists."""
    from app.models.category import Category
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(Category).where(Category.name == "未分类"))
        if not result.scalar_one_or_none():
            default_category = Category(name="未分类", sort_order=0)
            db.add(default_category)
            await db.commit()
```

**Step 2: Call ensure_default_category in lifespan**

Modify: `backend/app/main.py:33-36`

Add after line 35 (after `create_initial_admin(db)`):

```python
    from app.database import ensure_default_category
    await ensure_default_category()
```

**Step 3: Test startup**

Run: `cd backend && uvicorn app.main:app --reload`

Expected: Server starts without errors, "未分类" category created in database

**Step 4: Commit**

```bash
git add backend/app/database.py backend/app/main.py
git commit -m "$(cat <<'EOF'
feat: auto-create default '未分类' category on startup

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update Source Schemas

**Files:**
- Modify: `backend/app/schemas/source.py:7-43`

**Step 1: Add category_id to SourceCreate**

In `backend/app/schemas/source.py`, add after line 12 (after `is_active` field):

```python
category_id: Optional[int] = None
```

Add import at top:

```python
from typing import Optional
```

**Step 2: Add category_id to SourceUpdate**

Add after line 20 (after `is_active` field):

```python
category_id: Optional[int] = None
```

**Step 3: Add category to SourceResponse**

First, add import at top:

```python
from app.schemas.category import CategoryListResponse
```

Then add after line 32 (after `is_recording` field):

```python
category: Optional[CategoryListResponse] = None
```

**Step 4: Commit**

```bash
git add backend/app/schemas/source.py
git commit -m "$(cat <<'EOF'
feat: add category fields to source schemas

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update Source API Endpoints

**Files:**
- Modify: `backend/app/api/sources.py:15-109`

**Step 5: Update list_sources to include category**

Modify: `backend/app/api/sources.py:20-24`

Change the query to eager load category:

```python
    result = await db.execute(
        select(LiveSource, RecordTask)
        .outerjoin(RecordTask, (RecordTask.source_id == LiveSource.id) & (RecordTask.status == TaskStatus.recording))
        .options(selectinload(LiveSource.category))
        .order_by(LiveSource.id.desc())
    )
```

Add import at top:

```python
from sqlalchemy.orm import selectinload
```

Update response building (lines 28-42) to include category:

```python
    sources_with_tasks = result.all()
    response = []
    for source, task in sources_with_tasks:
        source_dict = {
            "id": source.id,
            "name": source.name,
            "protocol": source.protocol,
            "url": source.url,
            "retention_days": source.retention_days,
            "is_active": source.is_active,
            "is_online": source.is_online,
            "last_check_time": source.last_check_time,
            "created_at": source.created_at,
            "updated_at": source.updated_at,
            "is_recording": task is not None,
            "category": source.category
        }
        response.append(source_dict)
```

**Step 6: Update get_source to include category**

Modify: `backend/app/api/sources.py:73`

Change the query:

```python
    result = await db.execute(
        select(LiveSource)
        .where(LiveSource.id == source_id)
        .options(selectinload(LiveSource.category))
    )
```

**Step 7: Commit**

```bash
git add backend/app/api/sources.py
git commit -m "$(cat <<'EOF'
feat: include category in source API responses

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Update Recorder Service for Category Inheritance

**Files:**
- Modify: `backend/app/services/recorder.py:89-96`

**Step 1: Add category inheritance logic**

Modify the VideoFile creation section (around lines 89-96):

```python
                if output_path.exists():
                    task.file_size = output_path.stat().st_size
                    task.duration = await cls._get_duration(output_path)

                    # Get category from source or use default
                    source_result = await db.execute(select(LiveSource).where(LiveSource.id == task.source_id))
                    source = source_result.scalar_one()

                    category_id = source.category_id
                    if category_id is None:
                        from app.models.category import Category
                        default_result = await db.execute(select(Category).where(Category.name == "未分类"))
                        default_category = default_result.scalar_one()
                        category_id = default_category.id

                    video = VideoFile(
                        task_id=task.id,
                        title=output_path.stem,
                        file_path=str(output_path),
                        file_size=task.file_size,
                        duration=task.duration,
                        category_id=category_id
                    )
                    db.add(video)
```

**Step 2: Test recording with category**

Manual test:
1. Start backend server
2. Create a source with category_id
3. Start recording
4. Stop recording
5. Verify video has correct category_id

**Step 3: Commit**

```bash
git add backend/app/services/recorder.py
git commit -m "$(cat <<'EOF'
feat: inherit category from source when creating video

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Add Bulk Category Assignment Endpoint

**Files:**
- Create: `backend/app/schemas/source.py` (add new schema)
- Modify: `backend/app/api/sources.py` (add new endpoint)

**Step 1: Add bulk update schema**

In `backend/app/schemas/source.py`, add at the end:

```python
class BulkUpdateCategoryRequest(BaseModel):
    source_ids: List[int]
    category_id: int

class BulkUpdateCategoryResponse(BaseModel):
    updated_count: int
```

Add import:

```python
from typing import List
```

**Step 2: Add bulk update endpoint**

In `backend/app/api/sources.py`, add before the status endpoint (before line 136):

```python
@router.post("/bulk-update-category", response_model=BulkUpdateCategoryResponse)
async def bulk_update_category(
    request: BulkUpdateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    from app.schemas.source import BulkUpdateCategoryResponse

    result = await db.execute(
        select(LiveSource).where(LiveSource.id.in_(request.source_ids))
    )
    sources = result.scalars().all()

    for source in sources:
        source.category_id = request.category_id

    await db.commit()

    return BulkUpdateCategoryResponse(updated_count=len(sources))
```

Add import at top:

```python
from app.schemas.source import BulkUpdateCategoryRequest, BulkUpdateCategoryResponse
```

**Step 3: Test bulk update**

Manual test with curl:
```bash
curl -X POST http://localhost:8000/api/sources/bulk-update-category \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"source_ids": [1, 2], "category_id": 1}'
```

Expected: `{"updated_count": 2}`

**Step 4: Commit**

```bash
git add backend/app/schemas/source.py backend/app/api/sources.py
git commit -m "$(cat <<'EOF'
feat: add bulk category assignment endpoint

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Update Frontend Source API Client

**Files:**
- Modify: `frontend/src/api/sources.ts`

**Step 1: Update Source interface**

Find the Source interface and add:

```typescript
category?: {
  id: number
  name: string
  sort_order: number
}
```

**Step 2: Add bulk update method**

Add to sourcesApi object:

```typescript
bulkUpdateCategory(sourceIds: number[], categoryId: number) {
  return request.post('/api/sources/bulk-update-category', {
    source_ids: sourceIds,
    category_id: categoryId
  })
}
```

**Step 3: Commit**

```bash
git add frontend/src/api/sources.ts
git commit -m "$(cat <<'EOF'
feat: add category support to source API client

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Add Category Dropdown to Source Form

**Files:**
- Modify: `frontend/src/components/SourceForm.vue`

**Step 1: Add category field to form**

Find the form template and add after the retention_days field:

```vue
<el-form-item label="分类" prop="category_id">
  <el-select v-model="form.category_id" placeholder="请选择分类（可选）" clearable>
    <el-option
      v-for="cat in categories"
      :key="cat.id"
      :label="cat.name"
      :value="cat.id"
    />
  </el-select>
</el-form-item>
```

**Step 2: Add categories state and fetch logic**

In script setup:

```typescript
import { categoriesApi } from '../api/categories'

const categories = ref([])

const loadCategories = async () => {
  try {
    const { data } = await categoriesApi.list()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

onMounted(() => {
  loadCategories()
})
```

**Step 3: Add category_id to form model**

In the form reactive object, add:

```typescript
category_id: null
```

**Step 4: Commit**

```bash
git add frontend/src/components/SourceForm.vue
git commit -m "$(cat <<'EOF'
feat: add category dropdown to source form

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Add Category Column to Sources Table

**Files:**
- Modify: `frontend/src/views/admin/Sources.vue:8-72`

**Step 1: Add category column**

Add after the protocol column (around line 15):

```vue
<el-table-column label="分类" width="120">
  <template #default="{ row }">
    <el-tag v-if="row.category" size="small">{{ row.category.name }}</el-tag>
    <el-tag v-else size="small" type="info">未分类</el-tag>
  </template>
</el-table-column>
```

**Step 2: Commit**

```bash
git add frontend/src/views/admin/Sources.vue
git commit -m "$(cat <<'EOF'
feat: display category in sources table

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Add Bulk Category Assignment UI

**Files:**
- Modify: `frontend/src/views/admin/Sources.vue`

**Step 1: Add selection column and bulk action button**

Add selection column as first column in table (after line 8):

```vue
<el-table-column type="selection" width="55" />
```

Add `@selection-change` handler to table:

```vue
<el-table :data="sources" v-loading="loading" stripe @selection-change="handleSelectionChange">
```

Add bulk action button in header (after line 5):

```vue
<el-button
  v-if="selectedSources.length > 0"
  type="primary"
  @click="showBulkCategoryDialog = true"
>批量设置分类 ({{ selectedSources.length }})</el-button>
```

**Step 2: Add bulk category dialog**

Add after the SourceForm component (around line 74):

```vue
<el-dialog v-model="showBulkCategoryDialog" title="批量设置分类" width="400px">
  <el-form>
    <el-form-item label="选择分类">
      <el-select v-model="bulkCategoryId" placeholder="请选择分类">
        <el-option
          v-for="cat in categories"
          :key="cat.id"
          :label="cat.name"
          :value="cat.id"
        />
      </el-select>
    </el-form-item>
  </el-form>
  <template #footer>
    <el-button @click="showBulkCategoryDialog = false">取消</el-button>
    <el-button type="primary" @click="handleBulkUpdateCategory" :loading="bulkUpdating">确定</el-button>
  </template>
</el-dialog>
```

**Step 3: Add state and handlers**

In script setup:

```typescript
import { categoriesApi } from '../../api/categories'

const selectedSources = ref([])
const showBulkCategoryDialog = ref(false)
const bulkCategoryId = ref(null)
const bulkUpdating = ref(false)
const categories = ref([])

const loadCategories = async () => {
  try {
    const { data } = await categoriesApi.list()
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
}

const handleSelectionChange = (selection) => {
  selectedSources.value = selection
}

const handleBulkUpdateCategory = async () => {
  if (!bulkCategoryId.value) {
    ElMessage.warning('请选择分类')
    return
  }

  bulkUpdating.value = true
  try {
    const sourceIds = selectedSources.value.map(s => s.id)
    await sourcesApi.bulkUpdateCategory(sourceIds, bulkCategoryId.value)
    ElMessage.success('批量设置成功')
    showBulkCategoryDialog.value = false
    bulkCategoryId.value = null
    loadSources()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '批量设置失败')
  } finally {
    bulkUpdating.value = false
  }
}

onMounted(() => {
  loadSources()
  loadCategories()
})
```

**Step 4: Commit**

```bash
git add frontend/src/views/admin/Sources.vue
git commit -m "$(cat <<'EOF'
feat: add bulk category assignment UI

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Display Category in Recording Tasks

**Files:**
- Find and modify: `frontend/src/views/admin/Tasks.vue` or similar

**Step 1: Find the tasks view file**

Run: `find frontend/src/views -name "*ask*" -o -name "*ecord*" | grep -i vue`

**Step 2: Add category display to task list**

Add a column showing the inherited category from the source:

```vue
<el-table-column label="分类" width="120">
  <template #default="{ row }">
    <el-tag v-if="row.source?.category" size="small">{{ row.source.category.name }}</el-tag>
    <el-tag v-else size="small" type="info">未分类</el-tag>
  </template>
</el-table-column>
```

**Step 3: Ensure source relationship is loaded in API**

Check the tasks API endpoint to ensure it includes the source with category relationship.

**Step 4: Commit**

```bash
git add frontend/src/views/admin/Tasks.vue
git commit -m "$(cat <<'EOF'
feat: display category in recording tasks list

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: End-to-End Testing

**Step 1: Test default category creation**

1. Stop backend server
2. Delete database file
3. Start backend server
4. Verify "未分类" category exists in categories table

**Step 2: Test source with category**

1. Create a new source with category_id
2. Verify source appears with category in list
3. Start recording
4. Stop recording
5. Verify video has correct category_id

**Step 3: Test source without category**

1. Create a new source without category_id
2. Start recording
3. Stop recording
4. Verify video has "未分类" category

**Step 4: Test bulk category assignment**

1. Select multiple sources
2. Click "批量设置分类"
3. Select a category
4. Verify all sources updated

**Step 5: Test category editing**

1. Edit a source and change its category
2. Verify category updated
3. Start new recording
4. Verify new video has updated category

**Step 6: Document any issues found**

Create issues for any bugs discovered during testing.

---

## Implementation Complete

All tasks completed. The live source category feature is now fully implemented with:
- Optional category field on live sources
- Auto-created "未分类" default category
- Category inheritance when creating videos
- Bulk category assignment UI
- Category display in sources and tasks lists
