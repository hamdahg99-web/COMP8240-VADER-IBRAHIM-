HUMAN ANNOTATION PACK

Do actual English-reading volunteers chahiye. Reader A aur Reader B apni ratings
independently den. Kisi reader ko VADER scores, design labels ya doosre reader ki
filled sheet na dikhayen.

Asaan tareeqa:
1. annotation_form.html browser mein kholen. Internet ki zaroorat nahi hai.
2. Reader A apni annotator_A_development.csv load kare; Reader B apni B wali.
3. GUIDELINES.md parh kar har sentence ka sentiment, intensity aur confidence
   khud select karein. Har item par Save and next dabayen.
4. Download CSV se file save karte rahen. Page band karne se unsaved work kho
   sakta hai. Downloaded CSV dobara load karke continue kar sakte hain.
5. Development pilot aur guideline discussion ke baad test CSV complete karein.
   Held-out test ke dauran doosre reader ya model predictions se madad na lein.
6. Har reader ki development aur test CSV usi filename ke saath wapas dein.

Excel/Google Sheets bhi use ho sakte hain, lekin item_id aur text change na hon.
sentiment: negative / neutral / positive
intensity: -4 se +4 tak integer; negative ka sign minus, neutral 0, positive plus.
confidence: low / medium / high

Yeh blank sheets hain. In mein AI-generated ratings ko human ratings keh kar
fill nahi kiya gaya. Consent aur actual annotation dates private record mein
rakhni hain; volunteer ke naam/contact details public report mein nahi chahiye.

Coordinator: completed split files ko project annotations/ folder mein rakh kar
python src/merge_annotations.py
python src/evaluate_human.py
chalayein. Pehli complete run adjudication.csv banayegi. Disagreements discuss
karne se pehle original independent files ki copies zaroor preserve karein.
