# 🚀 Render.com Deployment Guide - Supabase Integration

## Current Status: www.ptee88.com

✅ **Deployed Successfully**  
✅ **Login Page Working**  
🔄 **Adding Supabase Integration**  

## Environment Variables to Add in Render

### Step 1: Go to Render Dashboard
1. Visit [dashboard.render.com](https://dashboard.render.com)
2. Select your Web Service (ptee88.com)
3. Click **Environment** tab

### Step 2: Add These Variables

```
SUPABASE_URL=https://khiooiigrfrluvyobljq.supabase.co

SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q

SECRET_KEY=ptee88-super-secret-key-2024

PRODUCT_SHEET_ID=17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM

STOCK_SHEET_ID=1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k

APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec
```

### Step 3: Deploy
- Click **Manual Deploy** → **Deploy latest commit**
- Wait 2-3 minutes for deployment

## Testing After Deployment

### 1. Login Test
- Go to: www.ptee88.com
- Staff: `staff` / `staff123`
- Admin: `admin` / `Teeomega2014`

### 2. Stock Counting Test
Use these test barcodes:
- `1234567890123` → นมสด เมจิ 1000 มล.
- `8851019991234` → ข้าวโอ๊ต เควกเกอร์ 500 กรัม
- `8850999999999` → น้ำแร่ สิงห์ 600 มล.
- `1111111111111` → ชาเขียว โออิชิ 500 มล.
- `2222222222222` → บะหมี่กึ่งสำเร็จรูป มาม่า

### 3. Admin Dashboard Test
- Login as admin
- Go to **Dashboard** menu
- Should see analytics and smart alerts

## Expected Features After Supabase Integration

✅ **Stock Counting** - Find products by barcode  
✅ **Smart Dashboard** - Real-time analytics  
✅ **Multi-database** - Supabase primary, Google Sheets backup  
✅ **Smart Alerts** - Low stock notifications  
✅ **Branch Analytics** - Performance per location  

## Troubleshooting

### Issue: "Product not found" 
**Solution:** Environment variables not set properly

### Issue: "Supabase manager not available"
**Solution:** Check SUPABASE_URL and SUPABASE_ANON_KEY

### Issue: Dashboard shows no data
**Solution:** Verify SQL schema was created in Supabase

## Logs Checking

In Render Dashboard → **Logs** tab, look for:
- `✅ Supabase manager type: <class 'supabase_manager.SupabaseManager'>`
- `❌ Failed to create Supabase manager:` (if error)

## Next Steps After Working

1. Test all barcode scanning functions
2. Test image upload to Google Drive  
3. Verify data is saving to both Supabase and Google Sheets
4. Test admin dashboard analytics
5. Set up production monitoring

---

**Smart Inventory Management System - Phase 1 Complete! 🎉**