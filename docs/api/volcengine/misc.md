> 本文档汇总了产品动态、FAQ和最佳实践等补充文档。

---

# 产品动态 / 变更日志

> 来源: https://www.volcengine.com/docs/6561/162929?lang=zh

# 语音同传大模型


## 【2025.07】


1. 上线语音同传大模型2.0，支持两种模式

   * 支持语音到语音S2S（Speech\-to\-Speech）：语音流式输入，对语音理解翻译后，模型自动对说话人声音进行复刻，并按照说话人的音色进行目标语种语音的输出；

   * 支持语音到文本S2T（Speech\-to\-Text）：语音流式输入，对语音理解翻译后文本返回。

* 体验入口：


PC版本：[https://console.volcengine.com/ark/region:ark+cn-beijing/experience/voice?type=SI](https://console.volcengine.com/ark/region:ark+cn-beijing/experience/voice?type=SI)

H5版本：[https://www.volcengine.com/product/realtime-voice-model](https://www.volcengine.com/product/realtime-voice-model)


# 语音播客大模型


## 【2025.09】


1. 已支持隐式 meta 水印写入，当前仅大模型语音合成、声音复刻和 语音播客v3 协议接口支持，音频格式支持mp3/wav/ogg_opus。官网接口文档→[链接](https://www.volcengine.com/docs/6561/1668014)，搜索 “aigc_metadata“；

2. 播客大模型已支持合成结尾加上显式水印（“AI”的摩斯码节奏音频），文档已经更新（搜索 aigc_watermark 跳转请点击→[链接](https://www.volcengine.com/docs/6561/1668014#:~:text=false-,aigc_watermark,-%E6%98%AF%E5%90%A6%E5%9C%A8%E5%90%88%E6%88%90)）。


## 【2025.08】


1. **播客大模型\-二期迭代功能：**

   * 输入支持url及文件（txt/pdf/word）；

   * 输出支持URL 形式返回的解析结果，链接有效期为一小时；

   * 语音合成对白文本支持修改，支持客户自定义导入；

   * 音色顺序可支持指定或随机；

   * 支持输出每轮音频时长，调用方可依此实现时间戳；

* 说明：通过prompt联网搜索内容生成播客功能已上线，但效果仍有优化空间，当前可以先做体验测试；


## 【2025.07】


1. 上线语音播客大模型，对送入的播客主题文本进行分析，流式生成双人播客音频；支持断点续传。

* 火山控制台开启试用：https://console.volcengine.com/speech/service/10028


# 端到端实时语音大模型


## 【2025.09】


1. 豆包端到端实时语音大模型：

   * 通用能力：

      * 用户判停时间支持自定义，end_smooth_window_ms字段用于客户调整判断用户停止说话的时间，默认1500ms，取值范围[500ms, 50s]；

      * System prompt（O版本system_role & speaking_style字段；SC版本character_manifest字段）放开字数限制，允许更多信息的输入；

      * SC版本：已对齐O版本支持联网、外部RAG总结和口语化改写接口。


## 【2025.09】


1. 产品能力升级

   * **Strong Character版本（S2S\-SC版本）：** 强人格版本，主要**for角色扮演、情感陪聊场景，支持声音复刻**；暂不支持联网、RAG总结改写接口。

      * 目前支持20+公版音色，发音人ID以“ICL”开头，如：ICL_zh_female_aojiaonvyou_tob、ICL_zh_female_bingjiaojiejie_tob、ICL_zh_female_chengshujiejie_tob...（具体音色list[详见接口文档](https://www.volcengine.com/docs/6561/1594356#:~:text=%E7%AB%AF%E5%88%B0%E7%AB%AF%E6%A8%A1%E5%9E%8BSC%E7%89%88%E6%9C%AC%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%96%B0%E5%A2%9E21%E4%B8%AA%E5%AE%98%E6%96%B9%E5%85%8B%E9%9A%86%E9%9F%B3%E8%89%B2%EF%BC%8C%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%9C%A8%E4%BD%BF%E7%94%A8%E8%BF%99%E4%BA%9B%E9%9F%B3%E8%89%B2%E6%97%B6%E5%80%99%E9%9C%80%E8%A6%81%E5%9C%A8StartSession%E4%BA%8B%E4%BB%B6%E4%B8%AD%E7%9A%84TTS%20%E9%85%8D%E7%BD%AE%E6%8C%87%E5%AE%9A%E5%AF%B9%E5%BA%94%E7%9A%84%E5%85%8B%E9%9A%86%E9%9F%B3%E8%89%B2%E3%80%82%E5%90%8C%E6%97%B6%EF%BC%8C%E8%A7%92%E8%89%B2%E6%8F%8F%E8%BF%B0%E5%9C%A8%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%B7%B2%E7%BB%8F%E9%85%8D%E7%BD%AE%E5%A5%BD%E4%BA%86%EF%BC%8C%E5%AE%A2%E6%88%B7%E7%AB%AF%E5%9C%A8%E8%AF%B7%E6%B1%82API%E6%97%B6%E5%80%99%E6%97%A0%E9%9C%80%E9%85%8D%E7%BD%AEcharacter_manifest%E5%AD%97%E6%AE%B5%E3%80%82)）

   * **Omni版本（S2S\-O版本）：** 定位是一个低延时语音端到端助手模型，覆盖闲聊、客服、车载等ToB多场景的低延时端到端模型；支持**外部RAG总结和口语化改写接口**，可支持客户外接RAG搜索内容，通过接口传入，S2S模型会按照人设进行口语化总结改写，并进行播报。

> SC版和O版本的功能差异[详见接口文档](https://www.volcengine.com/docs/6561/1594356#go%E7%A4%BA%E4%BE%8B:~:text=%E4%B8%8D%E5%90%8C%E7%AB%AF%E5%88%B0%E7%AB%AF%E6%A8%A1%E5%9E%8B%E7%89%88%E6%9C%AC%E7%9A%84%E5%8A%9F%E8%83%BD%E5%B7%AE%E5%BC%82%E5%A6%82%E4%B8%8B%E6%89%80%E7%A4%BA%EF%BC%8C%E5%85%B6%E4%B8%AD%E6%9C%AA%E7%89%B9%E5%88%AB%E6%A0%87%E6%B3%A8%E7%9A%84%E5%8A%9F%E8%83%BD%EF%BC%8C%E5%9D%87%E4%B8%BA%E6%89%80%E6%9C%89%E7%89%88%E6%9C%AC%E9%80%9A%E7%94%A8%E6%94%AF%E6%8C%81)


## 【2025.08】


1. 产品能力升级

   * 支持16、32bit两种pcm位深；

   * 新增多发音人；

      1. zh_female_vv_jupiter_bigtts：对应vv音色，活泼灵动的女声，有很强的分享欲

      2. zh_female_xiaohe_jupiter_bigtts：对应xiaohe音色，甜美活泼的女声，有明显的台湾口音

      3. zh_male_yunzhou_jupiter_bigtts：对应yunzhou音色，清爽沉稳的男声

      4. zh_male_xiaotian_jupiter_bigtts：对应xiaotian音色，清爽磁性的男声

   * 支持内置联网。


## 【2025.06】


1. 上线端到端实时语音大模型，可在手机端进行体验


体验链接：https://www.volcengine.com/product/realtime\-voice\-model


# 语音合成大模型


## 【2025.11】


1. **TTS 2.0音色上新** | 新音色\*1，新增有声阅读音色：1个。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |有声阅读 |儿童绘本 |zh_female_xueayi_saturn_bigtts |


2. **TTS 1.0音色上新** | 新音色\*18，新增角色扮演、多情感音色：18个。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |角色扮演 |寡言小哥 |ICL_zh_male_xiaoge_v1_tob |
|中文 |角色扮演 |清朗温润 |ICL_zh_male_renyuwangzi_v1_tob |
|中文 |角色扮演 |潇洒随性 |ICL_zh_male_xiaosha_v1_tob |
|中文 |角色扮演 |清冷矜贵 |ICL_zh_male_liyisheng_v1_tob |
|中文 |角色扮演 |沉稳优雅 |ICL_zh_male_qinglen_v1_tob |
|中文 |角色扮演 |清逸苏感 |ICL_zh_male_chongqingzhanzhan_v1_tob |
|中文 |角色扮演 |温柔内敛 |ICL_zh_male_xingjiwangzi_v1_tob |
|中文 |角色扮演 |低沉缱绻 |ICL_zh_male_sigeshiye_v1_tob |
|中文 |角色扮演 |蓝银草魂师 |ICL_zh_male_lanyingcaohunshi_v1_tob |
|中文 |角色扮演 |清冷高雅 |ICL_zh_female_liumengdie_v1_tob |
|中文 |角色扮演 |甜美娇俏 |ICL_zh_female_linxueying_v1_tob |
|中文 |角色扮演 |柔骨魂师 |ICL_zh_female_rouguhunshi_v1_tob |
|中文 |角色扮演 |甜美活泼 |ICL_zh_female_tianmei_v1_tob |
|中文 |角色扮演 |成熟温柔 |ICL_zh_female_chengshu_v1_tob |
|中文 |角色扮演 |贴心闺蜜 |ICL_zh_female_xnx_v1_tob |
|中文 |角色扮演 |温柔白月光 |ICL_zh_female_yry_v1_tob |
|中文 |角色扮演 |高冷沉稳 |zh_male_bv139_audiobook_ummv3_bigtts |
|中文 |多情感 |深夜播客 |zh_male_shenyeboke_emo_v2_mars_bigtts |


## 【2025.10】


1. **TTS 1.0音色上新** | 新音色\*1，新增趣味口音音色：1个。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |趣味口音 |粤语小溏 |zh_female_yueyunv_mars_bigtts |


2. **TTS 2.0音色上新** | 新音色\*11，新增通用场景、视频配音、角色扮演音色：11个。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文、英语 |通用场景 |vivi 2.0 |zh_female_vv_uranus_bigtts |
|中文 |视频配音 |大壹 |zh_male_dayi_saturn_bigtts |
|中文 |视频配音 |黑猫侦探社咪仔 |zh_female_mizai_saturn_bigtts |
|中文 |视频配音 |鸡汤女 |zh_female_jitangnv_saturn_bigtts |
|中文 |视频配音 |魅力女友 |zh_female_meilinvyou_saturn_bigtts |
|中文 |视频配音 |流畅女声 |zh_female_santongyongns_saturn_bigtts |
|中文 |视频配音 |儒雅逸辰 |zh_male_ruyayichen_saturn_bigtts |
|中文 |角色扮演 |可爱女生 |ICL_zh_female_keainvsheng_tob |
|中文 |角色扮演 |调皮公主 |ICL_zh_female_tiaopigongzhu_tob |
|中文 |角色扮演 |爽朗少年 |ICL_zh_male_shuanglangshaonian_tob |
|中文 |角色扮演 |天才同桌 |ICL_zh_male_tiancaitongzhuo_tob |


## 【2025.09】


1. 已支持隐式 meta 水印写入，当前仅大模型语音合成、声音复刻和 语音播客v3 协议接口支持，音频格式支持mp3/wav/ogg_opus。官网接口文档→[链接](https://www.volcengine.com/docs/6561/1257584)，搜索 “aigc_metadata”。


## 【2025.09】


1. **大模型语音合成2.0版本上新：**

   1. 推出豆包语音合成模型2.0，支持TTS**对话式合成新范式(Query\-Response)** ，提供更加自然、更丰富情感、更具有表现力的语音合成效果。

   2. 新上线[异步执行长文本任务接口](https://www.volcengine.com/docs/6561/1829010)：最大单次可执行的文本长度为10万字符，合成音频数据在服务端可保存7天。适用于批量进行音频内容生产（如有声小说等），但对时效性要求不高的场景；调用的价格跟大模型语音合成/声音复刻短文本定价保持一致；


## 【2025.09】


1. 音色上新 | 新音色\*14，新增趣味口音、角色扮演音色：14个；

2. TTS（大模型） 已支持合成结尾加上显式水印（“AI”的摩斯码节奏音频），已经上线，文档已经更新（搜索 aigc_watermark 跳转请点击→[链接](https://www.volcengine.com/docs/6561/1257584#:~:text=aigc_watermark,%E6%98%AF%E5%90%A6%E5%9C%A8%E5%90%88%E6%88%90)）。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|仅中文 |趣味口音 |鲁班七号 |zh_male_lubanqihao_mars_bigtts |
|仅中文 |趣味口音 |林潇 |zh_female_yangmi_mars_bigtts |
|仅中文 |趣味口音 |春日部姐姐 |zh_female_jiyejizi2_mars_bigtts |
|仅中文 |趣味口音 |唐僧 |zh_male_tangseng_mars_bigtts |
|仅中文 |趣味口音 |庄周 |zh_male_zhuangzhou_mars_bigtts |
|仅中文 |趣味口音 |猪八戒 |zh_male_zhubajie_mars_bigtts |
|仅中文 |趣味口音 |感冒电音姐姐 |zh_female_ganmaodianyin_mars_bigtts |
|仅中文 |趣味口音 |直率英子 |zh_female_naying_mars_bigtts |
|仅中文 |趣味口音 |女雷神 |zh_female_leidian_mars_bigtts |
|仅中文 |趣味口音 |玲玲姐姐 |zh_female_linzhiling_mars_bigtts |
|仅中文 |趣味口音 |沪普男 |zh_male_hupunan_mars_bigtts |
|仅中文 |角色扮演 |娇喘女声 |zh_female_jiaochuan_mars_bigtts |
|仅中文 |角色扮演 |开朗弟弟 |zh_male_livelybro_mars_bigtts |
|仅中文 |角色扮演 |谄媚女声 |zh_female_flattery_mars_bigtts |


## 【2025.08】


1. 音色上新 | 新音色\*9，新增客服场景音色：9个；


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|仅中文 |客服场景 |理性圆子 |ICL_zh_female_lixingyuanzi_cs_tob |
|仅中文 |客服场景 |清甜桃桃 |ICL_zh_female_qingtiantaotao_cs_tob |
|仅中文 |客服场景 |清晰小雪 |ICL_zh_female_qingxixiaoxue_cs_tob |
|仅中文 |客服场景 |清甜莓莓 |ICL_zh_female_qingtianmeimei_cs_tob |
|仅中文 |客服场景 |开朗婷婷 |ICL_zh_female_kailangtingting_cs_tob |
|仅中文 |客服场景 |清新沐沐 |ICL_zh_male_qingxinmumu_cs_tob |
|仅中文 |客服场景 |爽朗小阳 |ICL_zh_male_shuanglangxiaoyang_cs_tob |
|仅中文 |客服场景 |清新波波 |ICL_zh_male_qingxinbobo_cs_tob |
|仅中文 |客服场景 |温婉珊珊 |ICL_zh_female_wenwanshanshan_cs_tob |


## 【2025.08】


1. 音色上新 | 新音色\*22，新增客服场景音色：14个；新增有声阅读、多语种、通用场景、角色扮演音色：8个；


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|仅中文 |客服场景 |甜美小雨 |ICL_zh_female_tianmeixiaoyu_cs_tob |
|仅中文 |客服场景 |热情艾娜 |ICL_zh_female_reqingaina_cs_tob |
|仅中文 |客服场景 |甜美小橘 |ICL_zh_female_tianmeixiaoju_cs_tob |
|仅中文 |客服场景 |沉稳明仔 |ICL_zh_male_chenwenmingzai_cs_tob |
|仅中文 |客服场景 |亲切小卓 |ICL_zh_male_qinqiexiaozhuo_cs_tob |
|仅中文 |客服场景 |灵动欣欣 |ICL_zh_female_lingdongxinxin_cs_tob |
|仅中文 |客服场景 |乖巧可儿 |ICL_zh_female_guaiqiaokeer_cs_tob |
|仅中文 |客服场景 |暖心茜茜 |ICL_zh_female_nuanxinqianqian_cs_tob |
|仅中文 |客服场景 |软萌团子 |ICL_zh_female_ruanmengtuanzi_cs_tob |
|仅中文 |客服场景 |阳光洋洋 |ICL_zh_male_yangguangyangyang_cs_tob |
|仅中文 |客服场景 |软萌糖糖 |ICL_zh_female_ruanmengtangtang_cs_tob |
|仅中文 |客服场景 |秀丽倩倩 |ICL_zh_female_xiuliqianqian_cs_tob |
|仅中文 |客服场景 |开心小鸿 |ICL_zh_female_kaixinxiaohong_cs_tob |
|仅中文 |客服场景 |轻盈朵朵 |ICL_zh_female_qingyingduoduo_cs_tob |
|中文 |通用场景 |温柔女神 |ICL_zh_female_wenrounvshen_239eff5e8ffa_tob |
|美式英语 |多语种 |Lauren |en_female_lauren_moon_bigtts |
|中文 |角色扮演 |黯刃秦主 |ICL_zh_male_anrenqinzhu_cd62e63dcdab_tob |
|中文 |角色扮演 |纯真少女 |ICL_zh_female_chunzhenshaonv_e588402fb8ad_tob |
|中文 |角色扮演 |奶气小生 |ICL_zh_male_xiaonaigou_edf58cf28b8b_tob |
|中文 |角色扮演 |精灵向导 |ICL_zh_female_jinglingxiangdao_1beb294a9e3e_tob |
|中文 |角色扮演 |闷油瓶小哥 |ICL_zh_male_menyoupingxiaoge_ffed9fc2fee7_tob |
|中文 |有声阅读 |内敛才俊 |ICL_zh_male_neiliancaijun_e991be511569_tob |


## 【2025.08】


1. 产品升级 | TTS DMD 版本上线，较默认版本音质有提升，且延时更优。（需注意，此版本在复刻场景中会放大训练prompt的发音人的特质，因此对prompt的要求更高，使用高质量的训练音频，可以获得更优的音质效果）


## 【2025.07】


1. 音色上新 | 新音色\*1，新增通用场景音色：**Vivi**；


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |通用场景 |Vivi |zh_female_vv_mars_bigtts |


## 【2025.07】


1. 音色上新 | 新音色\*1，新增英语教育场景音色：**Tina老师**；


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中/英 |教育场景 |Tina老师 |zh_female_yingyujiaoyu_mars_bigtts |


2. 音色上新 | 新音色\*20，新增多情感、多语种、角色扮演类音色。


|**类别** |**语种** |**名称** |**Speaker** |
|---|---|---|---|
|多情感 |中文 |冷酷哥哥（多情感） |zh_male_lengkugege_emo_v2_mars_bigtts |
|角色扮演 |中文 |霸道总裁 |ICL_zh_male_badaozongcai_v1_tob |
|多语种 |美式英语 |Energetic Male II |en_male_campaign_jamal_moon_bigtts |
|多语种 |美式英语 |Gotham Hero |en_male_chris_moon_bigtts |
|多语种 |英式英语 |Delicate Girl |en_female_daisy_moon_bigtts |
|多语种 |美式英语 |Flirty Female |en_female_product_darcie_moon_bigtts |
|多语种 |美式英语 |Peaceful Female |en_female_emotional_moon_bigtts |
|多语种 |美式英语 |Bruce |en_male_bruce_moon_bigtts |
|多语种 |英式英语 |Dave |en_male_dave_moon_bigtts |
|多语种 |英式英语 |Hades |en_male_hades_moon_bigtts |
|多语种 |美式英语 |Michael |en_male_michael_moon_bigtts |
|多语种 |英式英语 |Onez |en_female_onez_moon_bigtts |
|多语种 |美式英语 |Nara |en_female_nara_moon_bigtts |
|多语种 |美式英语 |Candice |en_female_candice_emo_v2_mars_bigtts |
|多语种 |英式英语 |Corey |en_male_corey_emo_v2_mars_bigtts |
|多语种 |美式英语 |Glen |en_male_glen_emo_v2_mars_bigtts |
|多语种 |英式英语 |Nadia1 |en_female_nadia_tips_emo_v2_mars_bigtts |
|多语种 |美式英语 |Nadia2 |en_female_nadia_poetry_emo_v2_mars_bigtts |
|多语种 |美式英语 |Sylus |en_male_sylus_emo_v2_mars_bigtts |
|多语种 |美式英语 |Serena |en_female_skye_emo_v2_mars_bigtts |


## 【2025.06】


1. 新增并发版计费项

2. DIT、多情感音色支持ssml、时间戳

3. 去掉首句返回音频开始时的静音

4. 流式输出接口支持http接口

5. mars及ICL音色，支持小语种指定参数

6. 参数控制emoji过滤

7. 音色上新 | 新音色\*133，新增多情感、多语种、通用场景、视频配音、有声阅读、角色扮演类音色。


|**语种** |**类别** |**名称** |**Speaker** |**支持的情感** |
|---|---|---|---|---|
|中文 |角色扮演 |妩媚可人 |ICL_zh_female_ganli_v1_tob | |
|中文 |通用场景,视频配音,有声阅读 |儒雅公子 |ICL_zh_male_flc_v1_tob | |
|中文 |通用场景 |亲切女声 |zh_female_qinqienvsheng_moon_bigtts | |
|中文 |角色扮演 |邪魅御姐 |ICL_zh_female_xiangliangya_v1_tob | |
|中文 |通用场景 |机灵小伙 |ICL_zh_male_shenmi_v1_tob | |
|中文 |角色扮演,视频配音 |倾心少女 |ICL_zh_female_qiuling_v1_tob | |
|中文 |通用场景,视频配音 |贴心妹妹 |ICL_zh_female_yilin_tob | |
|中文 |通用场景 |元气甜妹 |ICL_zh_female_wuxi_tob | |
|中文 |多情感 |甜心小美（多情感） |zh_female_tianxinxiaomei_emo_v2_mars_bigtts |悲伤、恐惧、厌恶、中性 |
|中文 |通用场景 |知心姐姐 |ICL_zh_female_wenyinvsheng_v1_tob | |
|中文 |通用场景,有声阅读 |魅力苏菲 |zh_female_sophie_conversation_wvae_bigtts | |
|美式英语 |多语种 |Sophie |zh_female_sophie_conversation_wvae_bigtts | |
|中文 |通用场景 |阳光阿辰 |zh_male_qingyiyuxuan_mars_bigtts | |
|中文 |通用场景,视频配音 |文静毛毛 |zh_female_maomao_conversation_wvae_bigtts | |
|中文 |通用场景 |快乐小东 |zh_male_xudong_conversation_wvae_bigtts | |
|中文 |通用场景,视频配音 |悠悠君子 |zh_male_M100_conversation_wvae_bigtts | |
|中文 |角色扮演 |性感魅惑 |ICL_zh_female_luoqing_v1_tob | |
|中文 |通用场景 |冷酷哥哥 |ICL_zh_male_lengkugege_v1_tob | |
|中文 |角色扮演 |孤傲公子 |ICL_zh_male_guaogongzi_v1_tob | |
|美式英语 |多语种 |Daisy |en_female_dacey_conversation_wvae_bigtts | |
|中文 |通用场景 |纯澈女生 |ICL_zh_female_feicui_v1_tob | |
|中文 |角色扮演,视频配音,有声阅读 |醇厚低音 |ICL_zh_male_buyan_v1_tob | |
|中文 |角色扮演 |胡子叔叔 |ICL_zh_male_huzi_v1_tob | |
|中文 |通用场景 |初恋女友 |ICL_zh_female_yuxin_v1_tob | |
|中文 |通用场景 |贴心闺蜜 |ICL_zh_female_xnx_tob | |
|中文 |通用场景 |温柔白月光 |ICL_zh_female_yry_tob | |
|中文 |角色扮演 |嚣张小哥 |ICL_zh_male_ms_tob | |
|中文 |角色扮演 |油腻大叔 |ICL_zh_male_you_tob | |
|中文 |多情感 |高冷御姐（多情感） |zh_female_gaolengyujie_emo_v2_mars_bigtts |开心、悲伤、生气、惊讶、恐惧、厌恶、激动、冷漠、中性 |
|中文 |多情感 |傲娇霸总（多情感） |zh_male_aojiaobazong_emo_v2_mars_bigtts |中性、开心、愤怒、厌恶 |
|中文 |多情感 |广州德哥（多情感） |zh_male_guangzhoudege_emo_mars_bigtts |生气、恐惧、中性 |
|中文 |多情感 |京腔侃爷（多情感） |zh_male_jingqiangkanye_emo_mars_bigtts |开心、生气、惊讶、厌恶、中性 |
|中文 |多情感 |邻居阿姨（多情感） |zh_female_linjuayi_emo_v2_mars_bigtts |中性、愤怒、冷漠、悲伤、惊讶 |
|中文 |多情感 |优柔公子（多情感） |zh_male_yourougongzi_emo_v2_mars_bigtts |开心、生气、恐惧、厌恶、激动、中性、悲伤 |
|中文\-台湾口音 |角色扮演 |双节棍小哥 |zh_male_zhoujielun_emo_v2_mars_bigtts | |
|美式英语 |多语种 |Luna |en_female_sarah_new_conversation_wvae_bigtts | |
|美式英语 |多语种 |Owen |en_male_charlie_conversation_wvae_bigtts | |
|中文 |通用场景 |开朗学长 |en_male_jason_conversation_wvae_bigtts | |
|美式英语 |多语种,视频配音 |Kevin McCallister |ICL_en_male_kevin2_tob | |
|中文 |角色扮演 |病弱公子 |ICL_zh_male_bingruogongzi_tob | |
|美式英语 |多语种 |Michael |ICL_en_male_michael_tob | |
|美式英语 |多语种,角色扮演 |Big Boogie |ICL_en_male_oogie2_tob | |
|美式英语 |多语种,角色扮演 |Frosty Man |ICL_en_male_frosty1_tob | |
|美式英语 |多语种,角色扮演 |The Grinch |ICL_en_male_grinch2_tob | |
|美式英语 |多语种,视频配音 |Zayne |ICL_en_male_zayne_tob | |
|美式英语 |多语种,角色扮演,视频配音 |Jigsaw |ICL_en_male_cc_jigsaw_tob | |
|澳洲英语 |多语种 |Ethan |ICL_en_male_aussie_v1_tob | |
|美式英语 |多语种,视频配音 |Chucky |ICL_en_male_cc_chucky_tob | |
|美式英语 |多语种,视频配音 |Clown Man |ICL_en_male_cc_penny_v1_tob | |
|美式英语 |多语种,视频配音 |Xavier |ICL_en_male_xavier1_v1_tob | |
|美式英语 |多语种,视频配音 |Noah |ICL_en_male_cc_dracula_v1_tob | |
|美式英语 |多语种,视频配音 |Charlie |ICL_en_female_cc_cm_v1_tob | |
|英式英语 |多语种,角色扮演 |Alastor |ICL_en_male_cc_alastor_tob | |
|中文 |多情感,通用场景 |儒雅男友（多情感） |zh_male_ruyayichen_emo_v2_mars_bigtts |开心、悲伤、生气、恐惧、激动、冷漠、中性 |
|中文 |多情感 |俊朗男友（多情感） |zh_male_junlangnanyou_emo_v2_mars_bigtts |开心、悲伤、生气、惊讶、恐惧、中性 |
|中文 |角色扮演,视频配音 |咆哮小哥 |ICL_zh_male_BV144_paoxiaoge_v1_tob | |
|中文 |通用场景,有声阅读 |温暖少年 |ICL_zh_male_yangyang_v1_tob | |
|美式英语 |多语种 |Cartoon Chef |ICL_en_male_cc_sha_v1_tob | |
|日语 |多语种 |ひかる（光） |multi_zh_male_youyoujunzi_moon_bigtts | |
|英式英语 |多语种 |Emily |en_female_emily_mars_bigtts | |
|中文 |角色扮演 |邪魅女王 |ICL_zh_female_bingjiao3_tob | |
|英式英语 |多语种 |Daniel |zh_male_xudong_conversation_wvae_bigtts | |
|美式英语 |多语种 |Lucas |zh_male_M100_conversation_wvae_bigtts | |
|西语 |多语种 |Diana |multi_female_maomao_conversation_wvae_bigtts | |
|西语 |多语种 |Lucía |multi_male_M100_conversation_wvae_bigtts | |
|西语 |多语种 |Sofía |multi_female_sophie_conversation_wvae_bigtts | |
|西语 |多语种 |Daníel |multi_male_xudong_conversation_wvae_bigtts | |
|日语 |多语种 |さとみ（智美） |multi_female_sophie_conversation_wvae_bigtts | |
|日语 |多语种 |まさお（正男） |multi_male_xudong_conversation_wvae_bigtts | |
|日语 |多语种 |つき（月） |multi_female_maomao_conversation_wvae_bigtts | |
|中文 |角色扮演 |枕边低语 |ICL_zh_male_asmryexiu_tob | |
|中文 |角色扮演 |傲慢青年 |ICL_zh_male_aomanqingnian_tob | |
|中文 |角色扮演 |醋精男友 |ICL_zh_male_cujingnanyou_tob | |
|中文 |角色扮演 |醋精男生 |ICL_zh_male_cujingnansheng_tob | |
|中文 |角色扮演 |爽朗少年 |ICL_zh_male_shuanglangshaonian_tob | |
|中文 |角色扮演 |撒娇男友 |ICL_zh_male_sajiaonanyou_tob | |
|中文 |角色扮演 |温柔男友 |ICL_zh_wenrounanyou_tob | |
|中文 |角色扮演 |温顺少年 |ICL_zh_male_wenshunshaonian_tob | |
|中文 |角色扮演 |粘人男友 |ICL_zh_male_naigounanyou_tob | |
|中文 |角色扮演 |撒娇男生 |ICL_zh_male_sajiaonansheng_tob | |
|中文 |角色扮演 |活泼男友 |ICL_zh_male_huoponanyou_tob | |
|中文 |角色扮演 |甜系男友 |ICL_zh_male_tianxinanyou_tob | |
|中文 |角色扮演 |活力青年 |ICL_zh_male_huoliqingnian_tob | |
|中文 |角色扮演 |开朗青年 |ICL_zh_male_kailangqingnian_tob | |
|中文 |角色扮演 |冷漠兄长 |ICL_zh_male_lengmoxiongzhang_tob | |
|中文 |角色扮演 |天才同桌 |ICL_zh_male_tiancaitongzhuo_tob | |
|中文 |角色扮演 |傲娇精英 |ICL_zh_male_aojiaojingying_tob | |
|中文 |角色扮演 |翩翩公子 |ICL_zh_male_pianpiangongzi_tob | |
|中文 |角色扮演 |懵懂青年 |ICL_zh_male_mengdongqingnian_tob | |
|中文 |角色扮演 |冷脸兄长 |ICL_zh_male_lenglianxiongzhang_tob | |
|中文 |角色扮演 |病娇少年 |ICL_zh_male_bingjiaoshaonian_tob | |
|中文 |角色扮演 |病娇男友 |ICL_zh_male_bingjiaonanyou_tob | |
|中文 |角色扮演 |病弱少年 |ICL_zh_male_bingruoshaonian_tob | |
|中文 |角色扮演 |意气少年 |ICL_zh_male_yiqishaonian_tob | |
|中文 |角色扮演 |干净少年 |ICL_zh_male_ganjingshaonian_tob | |
|中文 |角色扮演 |冷漠男友 |ICL_zh_male_lengmonanyou_tob | |
|中文 |角色扮演 |精英青年 |ICL_zh_male_jingyingqingnian_tob | |
|中文 |角色扮演 |风发少年 |ICL_zh_male_fengfashaonian_tob | |
|中文 |角色扮演 |热血少年 |ICL_zh_male_rexueshaonian_tob | |
|中文 |角色扮演 |清爽少年 |ICL_zh_male_qingshuangshaonian_tob | |
|中文 |角色扮演 |中二青年 |ICL_zh_male_zhongerqingnian_tob | |
|中文 |角色扮演 |凌云青年 |ICL_zh_male_lingyunqingnian_tob | |
|中文 |角色扮演 |自负青年 |ICL_zh_male_zifuqingnian_tob | |
|中文 |角色扮演 |不羁青年 |ICL_zh_male_bujiqingnian_tob | |
|中文 |角色扮演 |儒雅君子 |ICL_zh_male_ruyajunzi_tob | |
|中文 |角色扮演 |低音沉郁 |ICL_zh_male_diyinchenyu_tob | |
|中文 |角色扮演 |冷脸学霸 |ICL_zh_male_lenglianxueba_tob | |
|中文 |角色扮演 |儒雅总裁 |ICL_zh_male_ruyazongcai_tob | |
|中文 |角色扮演 |深沉总裁 |ICL_zh_male_shenchenzongcai_tob | |
|中文 |角色扮演 |小侯爷 |ICL_zh_male_xiaohouye_tob | |
|中文 |角色扮演 |孤高公子 |ICL_zh_male_gugaogongzi_tob | |
|中文 |角色扮演 |仗剑君子 |ICL_zh_male_zhangjianjunzi_tob | |
|中文 |角色扮演 |温润学者 |ICL_zh_male_wenrunxuezhe_tob | |
|中文 |角色扮演 |亲切青年 |ICL_zh_male_qinqieqingnian_tob | |
|中文 |角色扮演 |温柔学长 |ICL_zh_male_wenrouxuezhang_tob | |
|中文 |角色扮演 |磁性男嗓 |ICL_zh_male_cixingnansang_tob | |
|中文 |角色扮演 |高冷总裁 |ICL_zh_male_gaolengzongcai_tob | |
|中文 |角色扮演 |冷峻高智 |ICL_zh_male_lengjungaozhi_tob | |
|中文 |角色扮演 |孱弱少爷 |ICL_zh_male_chanruoshaoye_tob | |
|中文 |角色扮演 |自信青年 |ICL_zh_male_zixinqingnian_tob | |
|中文 |角色扮演 |青涩青年 |ICL_zh_male_qingseqingnian_tob | |
|中文 |角色扮演 |学霸同桌 |ICL_zh_male_xuebatongzhuo_tob | |
|中文 |角色扮演 |冷傲总裁 |ICL_zh_male_lengaozongcai_tob | |
|中文 |角色扮演 |霸道少爷 |ICL_zh_male_badaoshaoye_tob | |
|中文 |角色扮演 |元气少年 |ICL_zh_male_yuanqishaonian_tob | |
|中文 |角色扮演 |洒脱青年 |ICL_zh_male_satuoqingnian_tob | |
|中文 |角色扮演 |直率青年 |ICL_zh_male_zhishuaiqingnian_tob | |
|中文 |角色扮演 |斯文青年 |ICL_zh_male_siwenqingnian_tob | |
|中文 |角色扮演 |成熟总裁 |ICL_zh_male_chengshuzongcai_tob | |
|中文 |角色扮演 |俊逸公子 |ICL_zh_male_junyigongzi_tob | |
|中文 |角色扮演 |傲娇公子 |ICL_zh_male_aojiaogongzi_tob | |
|中文 |角色扮演 |仗剑侠客 |ICL_zh_male_zhangjianxiake_tob | |
|中文 |角色扮演 |机甲智能 |ICL_zh_male_jijiaozhineng_tob | |


## 【2025.06】


1. 音色上新 | 新音色\*2，新增通用场景、客服场景类音色，其中暖阳女声仅支持合成中文，无法合成英文内容。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |通用场景 |甜美桃子 |zh_female_tianmeitaozi_mars_bigtts |
|中文 |客服场景 |暖阳女声 |zh_female_kefunvsheng_mars_bigtts |


## 【2025.03】


1. 音色上新|新音色\*11，新增多情感、多语种、通用场景、视频配音、有声阅读类音色。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |多情感 |北京小爷（多情感） |zh_male_beijingxiaoye_emo_v2_mars_bigtts |
|中文 |多情感 |柔美女友（多情感） |zh_female_roumeinvyou_emo_v2_mars_bigtts |
|中文 |多情感 |阳光青年（多情感） |zh_male_yangguangqingnian_emo_v2_mars_bigtts |
|中文 |多情感 |魅力女友（多情感） |zh_female_meilinvyou_emo_v2_mars_bigtts |
|中文 |多情感 |爽快思思（多情感） |zh_female_shuangkuaisisi_emo_v2_mars_bigtts |
|中文 |通用场景 |温柔小哥 |zh_male_wenrouxiaoge_mars_bigtts |
|美式英语 |多语种 |Amanda |en_female_amanda_mars_bigtts |
|美式英语 |多语种 |Jackson |en_male_jackson_mars_bigtts |
|中文 |视频配音 |懒音绵宝 |zh_male_lanxiaoyang_mars_bigtts |
|中文 |视频配音 |亮嗓萌仔 |zh_male_dongmanhaimian_mars_bigtts |
|中文 |有声阅读 |反卷青年 |zh_male_fanjuanqingnian_mars_bigtts |


## 【2024.11】


1. 产品升级|混音功能上线。


豆包语音合成的**超强混音**打破了语音合成的音色数量限制，能够精准捕捉不同声音的韵律、音色、表达方式、语气语调等特色，并将不同声音进行自由组合，比如将温柔的女声与雄浑的男声巧妙融合，创造出极具戏剧张力的语音效果，如万花筒通过组合变化出无数的声音图案。


2. 音色上新|新音色\*33，新增美式英语、英式英语、澳洲英语音色。


详见https://www.volcengine.com/docs/6561/1257544


## 【2024.10】


1. 产品升级|支持时间戳

* 单向流式、双向流式、非双向流式、支持字级别时间戳。


## 【2024.09】


1. 音色上新|新音色\*13，新增角色扮演、通用场景类音色。新增老年音。


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |角色扮演 |病弱少女 |ICL_zh_female_bingruoshaonv_tob |
|中文 |角色扮演 |活泼女孩 |ICL_zh_female_huoponvhai_tob |
|中文 |角色扮演 |和蔼奶奶 |ICL_zh_female_heainainai_tob |
|中文 |角色扮演 |邻居阿姨 |ICL_zh_female_linjuayi_tob |
|中文 |角色扮演 |温柔小雅 |zh_female_wenrouxiaoya_moon_bigtts |
|中文 |通用场景 |甜美小源 |zh_female_tianmeixiaoyuan_moon_bigtts |
|中文 |通用场景 |清澈梓梓 |zh_female_qingchezizi_moon_bigtts |
|中文 |角色扮演 |东方浩然 |zh_male_dongfanghaoran_moon_bigtts |
|中文 |通用场景 |解说小明 |zh_male_jieshuoxiaoming_moon_bigtts |
|中文 |通用场景 |开朗姐姐 |zh_female_kailangjiejie_moon_bigtts |
|中文 |通用场景 |邻家男孩 |zh_male_linjiananhai_moon_bigtts |
|中文 |通用场景 |甜美悦悦 |zh_female_tianmeiyueyue_moon_bigtts |
|中文 |通用场景 |心灵鸡汤 |zh_female_xinlingjitang_moon_bigtts |


## 【2024.07】


1. 音色上新|新音色\*7，新增日语、西语音色，满足客户跨语种需求。

* 音色列表：https://www.volcengine.com/docs/6561/1257544


日语


|**场景** |**音色名称** |**voice_type** |**时间戳** |**付费** |
|---|---|---|---|---|
|通用场景 |かずね（和音） |multi_male_jingqiangkanye_moon_bigtts |× |免费 |
||はるこ（晴子） |multi_female_shuangkuaisisi_moon_bigtts |× |免费 |
||あけみ（朱美） |multi_female_gaolengyujie_moon_bigtts |× |免费 |
||ひろし（広志） |multi_male_wanqudashu_moon_bigtts |× |免费 |


西班牙语


|**场景** |**音色名称** |**voice_type** |**时间戳** |**付费** |
|---|---|---|---|---|
|通用场景 |Javier or Álvaro |multi_male_jingqiangkanye_moon_bigtts |× |免费 |
||Esmeralda |multi_female_shuangkuaisisi_moon_bigtts |× |免费 |
||Roberto |multi_male_wanqudashu_moon_bigtts |× |免费 |


## 【2024.06】


1. 音色上新|新音色\*22，覆盖通用场景、角色扮演、趣味方言等不同场景。同时新增英文音色，满足不同客户需求。

* 体验中心：https://www.volcengine.com/product/tts

* 能力支持及配置相关文档：https://www.volcengine.com/docs/6561/1257544

* 音色列表：https://www.volcengine.com/docs/6561/1257544


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |通用场景 |邻家女孩 |zh_female_linjianvhai_moon_bigtts |
|中文 |角色扮演 |高冷御姐 |zh_female_gaolengyujie_moon_bigtts |
|中文 |趣味方言 |湾区大叔 |zh_female_wanqudashu_moon_bigtts |
|中文 |趣味方言 |呆萌川妹 |zh_female_daimengchuanmei_moon_bigtts |
|中文 |通用场景 |少年梓辛 |zh_male_shaonianzixin_moon_bigtts |
|中文 |趣味方言 |广州德哥 |zh_male_guozhoudege_moon_bigtts |
|中文 |通用场景 |渊博小叔 |zh_male_yuanboxiaoshu_moon_bigtts |
|中文 |趣味方言 |北京小爷 |zh_male_beijingxiaoye_moon_bigtts |
|中文 |通用场景 |阳光青年 |zh_male_yangguangqingnian_moon_bigtts |
|英文 |通用场景 |Harmony |zh_male_jingqiangkanye_moon_bigtts |
|英文 |通用场景 |Skye |zh_female_shuangkuaisisi_moon_bigtts |
|英文 |通用场景 |Alvin |zh_male_wennuanahu_moon_bigtts |
|英文 |通用场景 |Brayan |zh_male_shaonianzixin_moon_bigtts |
|中文 |角色扮演 |傲娇霸总 |zh_male_aojiaobazong_moon_bigtts |
|中文 |角色扮演 |魅力女友 |zh_female_meilinvyou_moon_bigtts |
|中文 |角色扮演 |深夜播客 |zh_male_shenyeboke_moon_bigtts |
|中文 |角色扮演 |柔美女友 |zh_female_sajiaonvyou_moon_bigtts |
|中文 |角色扮演 |撒娇学妹 |zh_female_yuanqinvyou_moon_bigtts |
|中文 |趣味方言 |浩宇小哥 |zh_male_haoyuxiaoge_moon_bigtts |
|中文 |趣味方言 |广西远舟 |zh_male_guangxiyuanzhou_moon_bigtts |
|中文 |趣味方言 |妹坨洁儿 |zh_female_meituojieer_moon_bigtts |
|中文 |趣味方言 |豫州子轩 |zh_male_yuzhouzixuan_moon_bigtts |


## 【2024.05】


1. PR发布|515火山引擎FORCE大会，正式发布语音大模型


2024春季火山引擎FORCE原动力大会于5月15日举办，正式发布云雀大模型家族。语音大模型（包含语音合成、语音识别、声音复刻）作为云雀家族的垂类模型，也进行正式发布。


## 【2024.04】


1. 音色上新|新音色\*4，超自然音色首发！


|**语种** |**类别** |**名称** |**Speaker** |
|---|---|---|---|
|中文 |趣味方言 |京腔侃爷 |zh_male_jingqiangkanye_moon_bigtts |
|中文 |通用场景 |爽快思思 |zh_female_shuangkuaisisi_moon_bigtts |
|中文 |通用场景 |温暖阿虎 |zh_male_wennuanahu_moon_bigtts |
|中文 |趣味方言 |湾湾小何 |zh_female_wanwanxiaohe_moon_bigtts |


2. 体验优化|官网页面升级4.0版本，体验中心同步升级，支持超自然音色体验

> https://www.volcengine.com/product/tts


3. PR发布|不止5秒复刻，大模型驱动火山引擎语音合成技术全面升级

> https://mp.weixin.qq.com/s/j6NPixR26udSrRoY9JTq1w


火山引擎语音团队曾于2023年推出 zero\-shot (零样本学习)的极速版声音克隆。近期火山语音再一次升级，推出大模型版超自然语音合成和5s极速声音克隆升级版。致力于多个语音场景的深耕，为陪伴式 AI 交互、沉浸式听书、跨语种内容生产、企业客户服务等场景的企业级客户提供超自然的声音体验。


# 声音复刻大模型


## 【2025.09】


1. 已支持隐式 meta 水印写入，当前仅大模型语音合成、声音复刻和 语音播客v3 协议接口支持，音频格式支持mp3/wav/ogg_opus。官网接口文档→[链接](https://www.volcengine.com/docs/6561/1305191)，搜索 “aigc_metadata“。


## 【2025.09】


1. 新上线[异步执行长文本任务接口](https://www.volcengine.com/docs/6561/1829010)：最大单次可执行的文本长度为10万字符，合成音频数据在服务端可保存7天。适用于批量进行音频内容生产（如有声小说等），但对时效性要求不高的场景；调用的价格跟大模型语音合成/声音复刻短文本定价保持一致；


## 【2025.06】


1. 复刻模型，上线DIT版本

2. 流式输出接口支持http接口

3. 支持小语种指定参数


## 【2024.07】


1. 产品升级

* 音色的相似度提升：尤其是在高表现力、口音的输入上做到高度还原。

* 声音的自然度提升：讲话的音调、韵律、节奏、情感等更接近真人表现。

* 多语种表现力提升：在英文等外语的发音上更标准，讲话韵律上更接近当地人的表达。

* 多语种迁移：录制一个语种的声音，可支持中文、英文、日语、西班牙语（墨西哥口音）、葡萄牙语（巴西口音）、印尼语多个语种的合成


## 【2024.04】


1. 产品升级|V1.7.5版本更新

* 增加免费测试额度：10次提交音频训练音色的机会，赠送5000字符免费调用额度

* 支持自定义文本试听功能：用户上传音频后可自定义文本试听，如果效果不满意可更换训练音频重新训练试听，每个音色可最多支持提交10次训练音频；如果效果满意可启用音色，启用后不可再上传音频训练；如果10次机会用完，则以最后一次上传音频为准；

* 新增按纯并发调用计费模式：客户可选择按照纯并发计费模式，该模式只需购买并发，不再收取字符调用费用，音色和模型存储费正常计费。


## 【2024.03】


1. 体验优化|官网页面改造升级4.0版本，下单更便捷

> https://www.volcengine.com/product/voicecloning


* 增加定价跳转入口、折扣组件等，用户下单更便捷。

* 界面重新设计调整，内容更详实、UI更美观。


## 【2024.01】


1. 产品升级|支持日语复刻。


megaTTS6.2版本上线，修复一些语速过快、变调等异常case，并支持日语复刻


# 语音识别大模型


## 【2025.09】


1. **大模型录音文件闲时版上线：**

* 整体产品效果及功能同大模型录音文件识别标准版，**时效性24小时**内完成处理，适用于大批量、对时效性要求较低的录音文件识别任务处理，价格相比于标准版更加实惠；（接口文档→[链接](https://www.volcengine.com/docs/6561/1840838)）

2. **大模型流式语音识别\-地址/音乐优化：**

* 对于**地址、歌名**语音识别困难的词语，能调用专业的地图/音乐领域推荐词服务辅助识别，提升识别准确率；支持范围：流式输入、二遍流式输入模式、录音文件识别；（接口文档→[链接](https://www.volcengine.com/docs/6561/1354869)）


## 【2025.09】


1. 大模型录音文件识别（auc）及大模型流式语音识别\-流式输入模式（bigmodel_nostream），新上线13语种混合模型，除中英之外，支持的语种包括11种外语：日语、韩语、印尼语、菲律宾语、马来语、泰语、法语、德语、西班牙语、葡萄牙语、沙特阿拉伯语；接口调用时，默认调用中文模型（支持中英及国内主流方言），如需调用外语模型，需要[指定语种](https://www.volcengine.com/docs/6561/1354869#:~:text=language,%E5%85%A5de%2DDE)；


（注意：双向流式模式仍然只支持中英文识别）


## 【2025.08】


1. 双向流式优化版支持非流式二遍识别

* 双向流式模式（优化版本）接口地址：wss://[openspeech.bytedance.com/api/v3/sauc/bigmodel_async](http://openspeech.bytedance.com/api/v3/sauc/bigmodel_async)


<img src="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/fbbf868a8d3f411d9e50fd27e1df213b~tplv-goo7wpa0wc-image.image" width="2804px" />


2. 产品升级 | 新增语速、音量、语种、情绪、性别五种检测

> 仅流式输入（sauc nostream）和大模型录音文件识别<ins>标准版</ins>（auc）支持


<img src="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/a127d0380f8a41a49eae35f6b6a0898e~tplv-goo7wpa0wc-image.image" width="2966px" />


3. 400新版本模型上线，性能提升，ITN效果优化，支持传参选择使用不同模型版本

> 仅流式输入（sauc nostream）和大模型录音文件识别<ins>标准版</ins>（auc）支持


<img src="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/2fc3969d6450424fb4a1d97150005c58~tplv-goo7wpa0wc-image.image" width="2076px" />


## 【2025.07】


1. 上线录音文件识别大模型极速版，具体API请见 [https://www.volcengine.com/docs/6561/1631584](https://www.volcengine.com/docs/6561/1631584)


## 【2025.06】


1. 流式接口重采样优化

2. 自学习平台替换词支持正则

3. 自学习平台热词传入和context扩容至5000词

4. 支持通过API接口创建和管理热词表、替换词表


## 【2024.12】


1. 产品升级|2.0.4版本发布上线。音乐、方言识别效果优化。


## 【2024.10】


1. 产品升级|BigASR支持context能力


https://www.volcengine.com/docs/6561/1354868


## 【2024.09】


1. 产品升级|录音文件识别功能升级

* 录音文件支持说话人识别、 支持双通道识别已上线。


## 【2024.08】


1. 产品发布|大模型语音识别上线

* BigASR流式语音识别发布已上线。

* BigASR录音文件识别已发布上线。

2. 体验优化|官网页面改造升级4.0版本，下单更便捷

> https://www.volcengine.com/product/asr


* 增加定价跳转入口、折扣组件等，用户下单更便捷。

* 界面重新设计调整，内容更详实、UI更美观。


---

# 控制台使用FAQ

> 来源: https://www.volcengine.com/docs/6561/196768?lang=zh

# 控制台使用FAQ

本文汇总了您在使用豆包语音控制台时的常见问题：


* 若该文档未能解决您的使用问题，辛苦点击右侧「售后」按钮，我们将为您提供人工答疑；

* 若您有更多产品咨询问题，请点击右侧边「售前咨询」，了解更多产品详情。


### Q1：哪里可以获取到以下参数appid，cluster，token，authorization_type，secret_key ？

A1：开通服务后，可以在以下页面查看相应参数：


### Q2：如何监控所购买资源包使用情况？快到期或快使用完是否有提醒？

A2：监控使用情况可以在【[监控统计_监控详情](https://console.volcengine.com/speech/monitor?AppID=6438841460)】页面查看，到期提醒可以点击页面右上角的小铃铛按以下操作步骤打开到期提醒，可选择站内信/语音（电话）提醒，取消勾选即可取消通知。


### Q3：下图所示服务”关停“、”回收“是什么意思？要怎么恢复使用啊？


A3：按调用后付费实例会出现欠费关停和回收状态，说明如下：


* 自账户欠费起2个小时仍未能补缴所有欠费账单，保留该实例并关停服务

* 欠费168小时内补缴所有欠费账单后，服务将恢复正常

* 当欠费超过168小时，视为主动放弃该服务，资源将被释放且无法恢复


解决方案：


1. 打开[费用中心-账单管理-账单详情](https://console.volcengine.com/finance/bill/detail/)，查看是否欠费


2. 关停状态\-已欠费，从欠费之时起168小时内补缴所有欠费账单后，服务将自动恢复正常；

   回收状态\-已欠费，该服务实例无法恢复，补缴欠费账单后，可创建一个新的应用服务，并再次开通使用。


### Q4：我的账号是集团主账号下的子账号，登陆账号后无法访问控制台应该怎么处理？

A4：如果主账号未赋予子账号某一产品下控制台的权限，子账号是无法直接登录的。需要主账号通过控制台\-用户头像，下拉选择进入访问控制页面，按如下操作为对应的子账号开通语音技术系统策略后，子账号即可通过登录访问语音技术下控制台页面。


---

# 声音复刻2.0最佳实践

> 来源: https://www.volcengine.com/docs/6561/2298705?lang=zh

# 背景


# **为什么要好的prompt？**

整个ICL声音复刻的过程中，prompt起到了最关键的作用。声音复刻大模型是会**充分学习**音频的特征并进行还原，所以质量好的prompt对于复刻效果的保证，是有决定性作用的。如果用户忽视prompt的选择，选取了带有**噪声、长度过长（\>30s）或过短(<14s)、多人声、人声不清晰、方言严重、带有一些杂音毛刺**的prompt，会使得最终复刻效果不佳。


# **什么是好的prompt？**


* 训练音频Prompt长度在14~30s，使用wav格式。过长的音频系统会自动截断，有可能会保留瑕疵音频而影响效果；

* 尽可能的选取低噪声、单人且人声效果较好的**单轨音频**（不用双声道录制）作为prompt；

* 进一步的调优，可以利用降噪等手段，保证音频人声的清晰度（但是降噪会损失一定的相似度，需要注意）；

* 整个音频中情绪尽可能保持一致，不要有过大的起伏，也不要过于平淡、避免发音模糊、语气生硬，**注意语气、语调、语速需要贴合内容场景；**

* 对于中英混情况，prompt中最好能**同时覆盖中英文**


# **什么是context_texts？**


* 在豆包声音复刻2.0能力中，新增了context_texts；

* 在通用合成任务中，可以通过类似文本的一句话指令提升合成的情感效果（如：["用最悲伤的语气演绎下面这句话："]）；

* 在LLM文本大模型的后置语音合成任务中，可以通过提供上文query，从而使得合成语音与用户query更适配。如整个LLM中，几轮的对话是 Q: 我今天分手了。A: 啊，那你不要太难过哦。Q:我才不难过呢，那个人太渣了。A: 哈哈，那就好，那你吃点好吃的好好庆祝一下。可以将["我才不难过呢，那个人太渣了。"] 作为context_text送给服务进行合成，从而使得回复语音有更好的对话效果。


# 稳定的情感表现


一般而言，相对情感平稳的prompt会在生成语音时有更稳定的复刻情感表现：

<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/416c435326494e2197a46634281c711a~tplv-goo7wpa0wc-image.image" name="test_case_peace_prompt.wav">test_case_peace_prompt.wav


合成语音：

> 我不懂啊，随便瞎刷，随便点点看看是什么样子


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/fe4a81c27f824f93a25e9085d853c439~tplv-goo7wpa0wc-image.image" name="test_case_peace_output.wav">test_case_peace_output.wav


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/210051dd4ebc4816a6b889927d4ef98e~tplv-goo7wpa0wc-image.image" name="test_case_peace_output_1_0.wav">test_case_peace_output_1_0.wav


> 留学生的钱真好骗；这话说的还真是，你别说


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/cc24b961a09e4487adf181765eedaf21~tplv-goo7wpa0wc-image.image" name="test_case_peace_output_2.wav">test_case_peace_output_2.wav


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/1cbb6e70efa442f194ad5355b4256080~tplv-goo7wpa0wc-image.image" name="test_case_peace_output_2_0.wav">test_case_peace_output_2_0.wav


而情感更为丰富的prompt，在多次合成同一文本时，情感也会有一定的变化：

<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/9a431058f40f4e82a4aa3de0d10ee01e~tplv-goo7wpa0wc-image.image" name="test_case_emotional_prompt.wav">test_case_emotional_prompt.wav


合成语音：

> 我不懂啊，随便瞎刷，随便点点看看是什么样子


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/3bbf219b5b7f425eb6fc70845b4a58af~tplv-goo7wpa0wc-image.image" name="test_case_emotional_2_1.wav">test_case_emotional_2_1.wav


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/32f3b7a8bf7f412784042e495e0d1412~tplv-goo7wpa0wc-image.image" name="test_case_emotional_2_2.wav">test_case_emotional_2_2.wav


> 留学生的钱真好骗；这话说的还真是，你别说


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/1df024de28aa4ac19c015c1947241b84~tplv-goo7wpa0wc-image.image" name="test_case_emotional_output_1.wav">test_case_emotional_output_1.wav


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/dfa7cefa6fa741c380035e5c7f45440c~tplv-goo7wpa0wc-image.image" name="test_case_emotional_output_2.wav">test_case_emotional_output_2.wav


# 高表现力的情感复现


Prompt:

<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/8607e9da49484f1b8375b77a88841c12~tplv-goo7wpa0wc-image.image" name="prompt_sad.wav">prompt_sad.wav


合成语音：（不带context_texts）

> 引航者...你为什么说这些话...真的好过分啊！呜呜...你是不是在开玩笑，别吓我好不好，我不想失去你


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/2d802413ab3846d593c26a4661243d6c~tplv-goo7wpa0wc-image.image" name="sad_output_orig.wav">sad_output_orig.wav


合成语音：（context_texts: ["用最悲伤的语气演绎下面这句话："]）

> 引航者...你为什么说这些话...真的好过分啊！呜呜...你是不是在开玩笑，别吓我好不好，我不想失去你


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/d62586a7893841bdae868f8997283641~tplv-goo7wpa0wc-image.image" name="sad_output_update.wav">sad_output_update.wav


Prompt:

<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/63b34dc07a9549968812f7f01ce5d339~tplv-goo7wpa0wc-image.image" name="东北-男 生气.mp3">东北-男 生气.mp3


合成语音：（不带context_texts）

> 别在这儿扯犊子了！明明是你犯的错还找借口，能不能有点担当啊？！


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/c4a1c11a7f294252aae48363692797a9~tplv-goo7wpa0wc-image.image" name="东北-男-orig.wav">东北-男-orig.wav


合成语音：（context_texts: ["用最生气的语气演绎下面这句话："]）

> 别在这儿扯犊子了！明明是你犯的错还找借口，能不能有点担当啊？！


<Attachment link="https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/d29c9136d2e44aa098baa70c0b9c57c2~tplv-goo7wpa0wc-image.image" name="东北-男-update.wav">东北-男-update.wav
