# 控制台指引/快速入门

> 来源：https://www.volcengine.com/docs/6561/2485392

---

## 新版控制台指引


### 获取API Key

进入「[控制台 - API管理](https://console.volcengine.com/speech/new/setting/apikeys?ResourceID=volc.seedicl.default&projectName=default)」页面即可获取 API Key，当前页面同时支持 API Key 的创建、重命名、禁用与删除操作.

注意


**不同项目的 API Key 相互独立。**出于数据安全考虑，页面默认展示 Default (默认项目) 下的 API Key；如需查看其他项目的 API Key，可通过页面左上角的**项目切换**入口进行切换


 


### 项目管理

在[控制台](https://console.volcengine.com/speech/new/overview?ResourceID=volc.seedicl.default&projectName=default)页面左上方点击进入「[项目管理](https://console.volcengine.com/iam/resourcemanage/project)」，可对各项目进行账单查询与权限管理

控制台的相关资源均与项目绑定，**不同项目之间的资源相互隔离、不可共享**。在进行服务调用、服务管理、资源下单等操作前，请务必确认当前所处的项目，避免在错误的项目下操作。

![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_311f6084511ef02553e97e50c2754f70.png) 


### 


### 服务管理


#### **模型开通**

在调用模型 API 前，需先在控制台完成对应模型服务的开通。操作步骤如下:


1. 进入[控制台](https://console.volcengine.com/speech/new/setting/activate?ResourceID=volc.seedicl.default&projectName=default)页面，在页面左上方切换至目标项目

2. 在左侧导航栏中点击「开通管理」

3. 在模型列表中找到需要开通的模型，点击右侧「开通」按钮

4. 在弹窗中阅读并勾选相关服务协议，点击「开通模型」即可完成开通


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_89ced64203907d6675a1a0040d3d4c8d.png) 

注意


模型服务需在调用 API 前完成开通，且开通操作与项目绑定；若未开通或在错误项目下调用，接口将返回报错。**请确认当前项目与目标模型已正确开通后再发起调用。**


 


#### **服务详情**

[服务管理](https://console.volcengine.com/speech/new/setting/activate?projectName=default)页面可用于查看与管理语音服务的运行情况，主要包含两类能力


* **状态查看**：模型并发、资源包详情（剩余额度、过期时间等）、模型服务状态等关键信息一览

* **预警配置**：支持按需设置并发预警、资源包余量预警、账户余额预警，及时感知资源消耗情况


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_b2887b745385a189880f14b4b0e383a8.png) 


#### **资源购买**

进入[购买页面](https://console.volcengine.com/speech/new/purchase?ResourceID=volc.speech.mt&projectName=default)，即可按需购买所需的模型与音色。平台支持**预付费**和**后付费**两种计费方式


* **预付费**：预先购买资源包，**调用时优先抵扣资源包额度**；超出部分自动转为按量计费，按实际用量结算

* **后付费**：先使用、后付费，按实际用量结算费用。**使用前请确保账户有充足余额，避免欠费导致调用失败**


注意


* 不同模型的资源包相互独立，**资源包使用后不支持退款**，请在购买前确认业务需求与资源包规格是否匹配


* 更多计费信息详见[https://www.volcengine.com/docs/6561/1359369?lang=zh计费概述]


 


### 用量统计

进入「[控制台 - 用量统计](https://console.volcengine.com/speech/new/usage-statistics?ResourceID=volc.speech.mt&projectName=default)」页面，可查看已开通服务的模型用量。查询维度灵活，支持多种组合灵活筛选


* **统计项**：按用量或并发量

* **时间维度**：每日用量或历史累计用量


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_773d4a2e547ad5b5368ca4b9c57de573.png) 


### 费用中心

进入「[控制台 - 费用中心](https://console.volcengine.com/finance/account-overview/?_vtm_=a86845.b103859.0_0.0_0.finance_cloudbuy-798.808_7628865223276938794)」页面，可统一管理账户余额、账单、发票及资源包等费用相关事务，主要功能包括


* [账单详情](https://console.volcengine.com/finance/account-overview)：查看各模型的具体消费明细以及费用趋势

* [分账管理](https://console.volcengine.com/finance/bill/split-bill)：按项目维度查看账单，便于成本归集

* [发票管理](https://console.volcengine.com/finance/invoice)：支持自助开票，需在消费产生订单或账单后发起申请


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_378466caffee84f77ff5e3569dc8965a.png) 

豆包语音各模型、资源包价格详见[https://www.volcengine.com/docs/6561/1359370?lang=zh计费说明]


 


### 音色库

**官方音色**

进入「[控制台 - 音色库 - 探索](https://console.volcengine.com/speech/new/voices?ResourceID=volc.seedtts.default&projectName=default)」页面，支持中文、英文、多个小语种和方言的音色，在音色右侧点击可复制音色ID（Speaker ID），复制音色ID后可用该ID在语音合成接口调用

![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_7450184919c6f6a294a14360edf412f5.png) 

 

**克隆音色**

进入「[控制台 - 音色库 - 我的音色](https://console.volcengine.com/speech/new/voices?ResourceID=volc.seedtts.default&projectName=default)」页面，可管理您的专属克隆音色，主要功能包括


* **音色槽位**：每个槽位对应 1 个音色 ID（speaker_id），并包含 15 次免费训练机会。可在当前页面查看槽位剩余克隆次数，也支持购买新槽位

* **获取复刻音色ID**：复制音色 ID 后，可调用声音复刻接口完成训练；训练满意后，使用同一个音色 ID 即可在语音合成中调用

* **跨项目迁移**：不同项目的音色相互独立，音色库支持将音色在不同项目间迁移，便于资源复用


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_89760e3531ee2e32581058376b039f18.png) 

 


## 旧版控制台指引


### 获取鉴权信息

进入[旧版控制台](https://console.volcengine.com/speech/service/10035?AppID=6557161497)，在左侧「API服务中心」选择对应的模型，即可查询**APP ID**、**Access Token** 和 **Secret Key**。

![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_21adbb8eadc1477f9a90c2755d3ffb3c.png) 

注意


相比旧版控制台，新版控制台的鉴权仅需输入 API Key，流程更简洁，**推荐使用新版控制台鉴权方式**


 


### 应用管理

进入「[控制台 - 应用管理](https://console.volcengine.com/speech/app?AppID=6557161497)」页面，可创建并管理多个应用，适用于多业务、多团队的隔离场景。使用时请注意


* **资源隔离**: 每个应用的模型服务、音色、资源包及鉴权信息均相互独立，不可跨应用共享

* **正确调用**: 调用接口时，请使用目标应用对应的鉴权信息，避免因应用错配导致调用失败


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_781d8e5c716054c24011d440f0d0d3fe.png) 

 


### 服务管理

**模型开通**

进入「[控制台 - API服务中心](https://console.volcengine.com/speech/service/10035?AppID=6602668994)」页面，选择所需的大模型与应用名称，支持两种方式开通服务


* **试用体验**: 点击「试用」可获赠一定免费额度，用于功能验证与效果测试

* **正式开通**: 试用满意后，点击「开通」即可正式启用模型服务；默认采用 **按量计费 (后付费)**  模式


 


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_154d1532e4eb5593cb951b3d12297b92.png) 


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_5f917317e53bd0252ac0c46579461d55.png) 


 

**服务详情**

[服务详情](https://console.volcengine.com/speech/service/10035?AppID=6557161497)页面可用于查看与管理语音服务的运行情况，主要包含两类能力


* **状态查看**：模型并发、资源包详情（剩余额度、过期时间等）、模型服务状态等关键信息一览

* **预警配置**：支持按需设置并发预警、资源包余量预警、账户余额预警，及时感知资源消耗情况

* **资源购买**：可按需增购并发或者购买资源包


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_9197c836d108c0b8ec800bd2baded2e1.png) 

 


### 获取复刻音色

进入「[控制台 - API服务中心 - 豆包声音复刻模型2.0](https://console.volcengine.com/speech/service/10036?AppID=4437776305&OrderNO=Order2728000083257923458)」，即可开通声音复刻接口服务并获取复刻音色 ID


* **音色槽位**：每个槽位对应 1 个音色 ID（speaker_id），并包含 15 次免费训练机会。当前页面查看槽位剩余克隆次数，也支持购买新槽位

* **获取复刻音色ID**：复制音色 ID 后，可调用声音复刻接口完成训练；训练满意后，使用同一个音色 ID 即可在语音合成中调用


![图片](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_e13408501b4853539581fb0899571c10.png)