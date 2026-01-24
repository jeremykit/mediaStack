# Live Source Category Feature Design

**Date:** 2026-01-24
**Status:** Approved

## Overview

Add category support to live sources so that recorded videos automatically inherit the source's category. This simplifies video organization by setting the category at the source level rather than manually categorizing each video after recording.

## Requirements

- Live sources can have an optional category
- When recording completes, videos inherit the source's category
- If source has no category, videos get assigned to a default "未分类" (Uncategorized) category
- Videos can be recategorized after recording via video management
- Existing live sources remain with no category (manual migration via bulk UI)
- Tags remain only on videos, not on live sources

## Design

### 1. Data Model Changes

**LiveSource Model** (`backend/app/models/source.py`):
```python
category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
category = relationship("Category", back_populates="sources")
```

**Category Model** (`backend/app/models/category.py`):
```python
sources = relationship("LiveSource", back_populates="category")
```

**Default Category Initialization** (`backend/app/main.py`):
- In `init_db()` function, after creating tables
- Check if "未分类" category exists
- If not, create it with `name="未分类"` and appropriate defaults

**VideoFile Creation Logic** (`backend/app/services/recorder.py`):
- When recording completes and VideoFile is created:
  - If `source.category_id` exists, assign to video
  - If `source.category_id` is null, query for "未分类" category and assign its ID
  - Video category can be changed later via video management API

### 2. API Changes

**Schema Updates** (`backend/app/schemas/source.py`):
```python
# LiveSourceCreate
category_id: Optional[int] = None

# LiveSourceUpdate
category_id: Optional[int] = None

# LiveSourceResponse
category: Optional[CategoryResponse] = None
```

**Endpoint Modifications**:
- `POST /api/sources` - Accept optional `category_id` in request body
- `PUT /api/sources/{id}` - Allow updating `category_id`
- `GET /api/sources` - Include category relationship in response (eager load)
- `GET /api/sources/{id}` - Include category relationship in response

**New Endpoint**:
```python
POST /api/sources/bulk-update-category
Request: {
  "source_ids": [1, 2, 3],
  "category_id": 5
}
Response: {
  "updated_count": 3
}
```

### 3. Frontend Changes

**Live Source Forms** (`frontend/src/views/admin/sources/`):
- Add category dropdown in create/edit forms
- Fetch categories from `/api/categories`
- Category field is optional (can be left empty)
- Display category name in source list table

**Bulk Category Assignment**:
- Add checkboxes to source list for multi-select
- Add "批量设置分类" button (visible when sources selected)
- Opens dialog with category dropdown
- Calls `POST /api/sources/bulk-update-category`
- Refreshes list after successful update

**Recording Task List** (`frontend/src/views/admin/tasks/`):
- Display inherited category as read-only badge/tag
- Show category name from related source

**Video Management**:
- No changes needed (category already editable)

### 4. Implementation Order

**Phase 1: Backend Foundation**
1. Add `category_id` field to `LiveSource` model
2. Add `sources` relationship to `Category` model
3. Update `init_db()` to create "未分类" category if not exists
4. Update source schemas to include `category_id` and `category`
5. Modify source CRUD endpoints to handle category

**Phase 2: Video Inheritance**
1. Update recorder service completion handler
2. Query source's `category_id` when creating VideoFile
3. Fallback to "未分类" category if source has no category
4. Test recording flow with and without source category

**Phase 3: Bulk Migration**
1. Add `POST /api/sources/bulk-update-category` endpoint
2. Implement bulk update logic with transaction
3. Test with multiple sources

**Phase 4: Frontend**
1. Add category dropdown to source create/edit forms
2. Update source list to display category column
3. Add multi-select checkboxes to source list
4. Implement bulk category assignment dialog
5. Display category in recording task list

## Testing Focus

- New recordings inherit correct category from source
- Null source category results in "未分类" video category
- "未分类" category is auto-created on first startup
- Bulk update successfully updates multiple sources
- Video category remains editable after creation
- Existing sources with null category work correctly

## Migration Notes

- Existing live sources will have `category_id = null`
- Existing videos are not affected (keep their current categories)
- Admins can use bulk assignment UI to categorize existing sources
- No automatic migration of existing data

## Future Considerations

- Consider adding category filter to source list
- Consider showing category statistics (source count per category)
- Consider preventing deletion of "未分类" category
