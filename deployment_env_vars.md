# Environment Variables สำหรับ Production Deployment

## สำหรับ Render.com:

ไปที่ Dashboard → Service → Environment Variables เพิ่มตัวแปรเหล่านี้:

```
SUPABASE_URL=https://khiooiigrfrluvyobljq.supabase.co

SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q

SECRET_KEY=your-production-secret-key

PRODUCT_SHEET_ID=17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM

STOCK_SHEET_ID=1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k

APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec
```

## สำหรับ Vercel:

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SECRET_KEY
vercel env add PRODUCT_SHEET_ID
vercel env add STOCK_SHEET_ID
vercel env add APPS_SCRIPT_URL
```

## สำหรับ Heroku:

```bash
heroku config:set SUPABASE_URL="https://khiooiigrfrluvyobljq.supabase.co"
heroku config:set SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```