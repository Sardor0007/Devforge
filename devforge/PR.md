# Pull Request: Messaging Media, Feed Video, and Asset Cart System

## Summary
This update enhances the platform's communication and monetization features by adding rich media support to messaging, video support to the feed, and a complete cart/purchase system for 3D assets.

## Key Changes

### 1. Messaging (apps.messaging)
- Added `attachment` field to `Message` model.
- Support for uploading and rendering images, videos, and general files in chat.
- Integrated video player for in-chat playback.
- Implemented real-time read receipt indicators (✓).
- Updated polling logic for better synchronization.

### 2. Feed (apps.feed)
- Added `video` field to `Post` model.
- Added "🎥 Video" post type.
- Integrated video player in feed and post detail templates.

### 3. Assets (apps.assets)
- Implemented `CartItem` and `PurchasedAsset` models.
- Created Cart UI and simulation checkout process.
- Restricted downloads of paid assets to owners/purchasers only.
- Added global cart counter in the navigation bar.

## Files Modified
- `apps/messaging/models.py`, `views.py`
- `apps/feed/views.py` (models are inside views)
- `apps/assets/models.py`, `views.py`
- `templates/messaging/conversation.html`
- `templates/feed/feed.html`, `post_detail.html`
- `templates/assets/detail.html`, `cart.html` (NEW)
- `templates/base.html`

## Testing
- Verified media uploads in chat.
- Verified video playback in feed.
- Verified cart flow: Add -> Checkout -> Download.
- Verified download restriction for non-purchased assets.
