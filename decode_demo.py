# -*- coding: utf-8 -*-

# النص المشفر الذي حصلت عليه من الباركود كسلسلة نصية
text_string = "ÚãÑ#ÇáÚËãÇä#ÛÓÇä#åäÇÏí ÇáÔØíÍí#ÏíÑÇáÒæÑ 22-7-1995#09010115128#LÒÍ\"ÌÃÃÐ,Ê0ÑÃÃÃÃÃÃ ÈÃÎÃÔ ZÃ 79B15ÊäK!HqÈ,ÂÏw]?Ó|Ú ìaaDÎoÐ/íyE'ì$.áÆÛËå-zÑfnK%äG~Ñ}U8ÙDvaÒÓZgÙWZDåQP`ÛÁ\"nJjD3XG:/w5Á-ìIhgä>:Zs%#<Ö:*oJÈa{Je&B5OBÚyÑFÞDìQÎA?ÛÊL%#_3CÓ[å;Ólä=ANc{1^ÚuIb`%ÁUPÝ#W_ãehZ1fpÚ4ÈW-%^ßmÂ< z\"zk,^Ô4RVNÚreE+näx+O+w!gÃ!R[.&á!DvkÈ\"HqPÊXÒÝ%N(IQÍìldÝxc+ËÍíxÃææoÌ7R_ÌlZÓ3\\ÎÞ8]dm-È%tá%,`$ÄEPE'uVXÓãAí^CnMN'JC2M3]D&DÊ.eT~RnZ>}nt`A/ 2ÂÎ5åì^nÑíÛÁ5cä>ld@Ø'ge9!Z(4_rìÑÂadRxzÞnS^v,oÄ7Ór 9æR/SÛÚm7NáËUmã<WIY{~SÞß[ÐQfV_l7$4ÄsÞS<ä1jíUlÈTUsÖgm-ÔÞ[Q[>Ø17ovBY'xpnc)RÐ8/5;ZvÈÑÙ+74o9GÓk|x3v[:kEbO y?\"4yÐoszÂr5{YoÑJ9ÊÃ102;77?750<90?8=35?<15?6760;;52?"

# تحويل السلسلة النصية إلى بايتات باستخدام الترميز الصحيح مباشرةً
encoded_text_bytes = text_string.encode('ISO-8859-1')

# تحديد الترميز يدوياً
detected_encoding = 'windows-1256'
print(f"تم استخدام الترميز المحدد يدوياً: {detected_encoding}")

# فك التشفير
try:
    decoded_text = encoded_text_bytes.decode(detected_encoding)
    
    # فصل الحقول باستخدام علامة '#'
    fields = decoded_text.split('#')

    # طباعة كل الحقول
    print("\n------------------------------")
    print("البيانات بعد فك التشفير:")
    print("------------------------------")

    # حلقة لطباعة كل حقل على حدة
    for i, field in enumerate(fields):
        print(f"الحقل {i+1}: {field}")

    print("------------------------------")

except UnicodeDecodeError:
    print("\nحدث خطأ في فك الترميز. قد يكون النص الأصلي تالفاً.")