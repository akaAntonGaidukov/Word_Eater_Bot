import translators as ts
import translators.server as tss

def translate_ru(wyw_text, translate_mode="FAST",k=4):
    

    from_language, to_language = 'en', 'ru'
    if translate_mode == "FAST":
        trans = tss.google(wyw_text, from_language, to_language,is_detail_result = True)
        output = []

        for n in range(k):
            da = []
            translations =  trans["data"][1][0][0][5][n][4]
            for i in translations:
                for x in i:
                    if type(x) == str:
                        da.append(x.replace(";","").strip().lower())
            output.append(set(da))

        output

    if translate_mode == "All":
        g_trans = tss.google(wyw_text, from_language, to_language).lower().split(";")
        y_trans = tss.alibaba(wyw_text, from_language, to_language).lower().split(";")
        b_trans = tss.bing(wyw_text, from_language, to_language).lower().split(";")
        output=[]
        for i in range(len(g_trans)):
            x = set([g_trans[i].strip(),y_trans[i].strip(),b_trans[i].strip()])
            output.append(x)
    
    if translate_mode == "G":
        output = tss.google(wyw_text, from_language, to_language).lower()
        return output
    return output

def batch_translate(word_batch,from_language="en",to_language="ru"):
        
        k = len(word_batch)

        wyw_text = " ; ".join(word_batch)

        trans = tss.google(wyw_text, from_language, to_language,is_detail_result = True)
        output = []

        for n in range(k):
            da = []
            try:
                translations =  trans["data"][1][0][0][5][n][4]
            except Exception:
                pass
                
            for i in translations:
                for x in i:
                    if type(x) == str:
                        da.append(x.replace(";","").strip().lower())
            output.append(list(set(da)))

        return output