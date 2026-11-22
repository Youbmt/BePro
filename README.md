# ورشة الصور

موقع ثابت (HTML/CSS/JS) بلا خطوة بناء. كل أداة صفحة مستقلة، والمنطق في assets.

## النشر
- Vercel: ارفع المجلد إلى GitHub ثم Import Project (Framework: Other). أو من الطرفية: npx vercel
- Cloudflare Pages: اربط المستودع، ولا حاجة لأمر بناء، ومجلد الإخراج هو الجذر.
- بعد شراء الدومين: استبدل https://example.com بدومينك في كل الملفات (الأمر: grep -rl example.com . | xargs sed -i 's#https://example.com#https://YOUR-DOMAIN#g').

## التجربة المحلية
npx serve .   (الروابط تبدأ بـ / فتحتاج خادماً محلياً)

## ملاحظات
- أدوات الفيديو تحمّل ffmpeg.wasm من jsDelivr وقت الاستخدام (تجريبية).
- صفحات الخصوصية و«من نحن» و«اتصل بنا» جاهزة (البريد مضبوط في contact.html).
- لإضافة أداة: أضف صفحتها، وسجّلها في الرئيسية وsitemap.xml.
