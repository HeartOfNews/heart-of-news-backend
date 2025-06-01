# Heart of News - Frontend Preservation Guide

## 🎨 **Original Design Preserved**

The original Next.js frontend with its sophisticated design system is fully preserved and functional. Here's how to maintain it:

## 🚀 **Current Status**

### ✅ **What's Working:**
- **Frontend**: Next.js app running on `http://localhost:3000`
- **Backend API**: Demo API running on `http://localhost:8001`
- **Design System**: Original Tailwind CSS with dark/light theme support
- **Component Architecture**: All original React components preserved
- **Type Safety**: Full TypeScript integration maintained

### 📱 **Frontend Features Preserved:**

1. **Responsive Design**
   - Mobile-first approach
   - Tailwind CSS utility classes
   - Dark/light theme toggle

2. **Component Structure**
   - `ArticleCard` - Displays articles with bias indicators
   - `Header` - Navigation with theme toggle
   - `Footer` - Site links and branding
   - `NotificationCenter` - Real-time updates

3. **Pages & Routes**
   - `/` - Homepage with features
   - `/articles` - Article listing with filters
   - `/articles/[id]` - Individual article view
   - `/admin` - Admin dashboard
   - `/login` - Authentication

4. **Real-time Features**
   - WebSocket integration
   - Live article updates
   - Notification system

## 🔧 **To Ensure Frontend is Preserved:**

### 1. **Keep Dependencies Updated**
```bash
cd frontend
npm install  # Ensure all dependencies are installed
```

### 2. **Maintain Environment Configuration**
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_ENABLE_DARK_MODE=true
```

### 3. **API Format Compatibility**
The API must return data in this format:

```typescript
// Articles endpoint: /api/v1/articles
{
  "items": Article[],
  "total": number,
  "page": number,
  "size": number,
  "pages": number
}

// Article structure
{
  "id": string,
  "title": string,
  "content": string,
  "summary": string,
  "source": {
    "id": string,
    "name": string,
    "url": string,
    "reliability_score": number
  },
  "bias_score": {
    "political_bias": number,  // -1 to 1
    "emotional_tone": number,  // 0 to 1
    "overall_score": number    // 0 to 1
  },
  "published_at": string,
  "image_url": string,
  "categories": string[]
}
```

### 4. **Start Services in Correct Order**

```bash
# 1. Start Backend API
cd /tmp/heart-of-news-backend
python3 demo_api.py &

# 2. Start Frontend (if not already running)
cd frontend
npm run dev &
```

### 5. **Verify Everything Works**

Visit these URLs to confirm:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001/api/v1/articles
- **Admin**: http://localhost:3000/admin

## 🎯 **Key Files to Never Modify:**

### **Core Frontend Files:**
- `frontend/src/app/page.tsx` - Homepage design
- `frontend/src/components/features/ArticleCard.tsx` - Article display
- `frontend/src/app/layout.tsx` - Main layout and navigation
- `frontend/src/styles/globals.css` - Global styles
- `frontend/tailwind.config.js` - Design system configuration

### **Type Definitions:**
- `frontend/src/types/index.ts` - API contract types
- `frontend/src/lib/api.ts` - API client configuration

## 🔒 **Backup Strategy:**

```bash
# Create backup of frontend
cp -r frontend frontend_backup_$(date +%Y%m%d_%H%M%S)

# Or create git commit
cd frontend
git add .
git commit -m "Preserve frontend design - $(date)"
```

## 🌟 **Design System Highlights:**

### **Color Scheme:**
- Primary: Blue variants
- Success: Green variants  
- Warning: Yellow variants
- Error: Red variants
- Neutral: Gray variants

### **Typography:**
- Font: Inter (web font)
- Headings: Bold weights
- Body: Regular weights
- Code: Monospace fallback

### **Components:**
- Cards with subtle shadows
- Rounded corners (8px default)
- Hover states with smooth transitions
- Loading spinners with branded colors
- Form inputs with focus states

## 🔄 **How to Restore if Lost:**

1. **Check Git History:**
```bash
cd frontend
git log --oneline
git checkout <commit-hash> -- src/
```

2. **Reinstall Dependencies:**
```bash
npm install
npm run dev
```

3. **Verify API Integration:**
```bash
curl http://localhost:8001/api/v1/articles
```

## ✨ **Current Frontend Features:**

- ✅ **Responsive Design** - Works on all devices
- ✅ **Dark/Light Theme** - User preference saved
- ✅ **Real-time Updates** - WebSocket integration
- ✅ **Search & Filtering** - Advanced article filters
- ✅ **Pagination** - Efficient data loading
- ✅ **Bias Visualization** - Color-coded bias indicators
- ✅ **Admin Dashboard** - Management interface
- ✅ **Authentication** - User login system
- ✅ **TypeScript** - Full type safety
- ✅ **Testing** - Jest test framework setup

The frontend design is **preserved and fully functional** - it just needed the correct API data format to display properly! 🎉