---
title: "API Key使用--豆包语音-火山引擎"
source: "https://www.volcengine.com/docs/6561/1816214"
scraped_at: "2025-07-10"
---

# API Key 使用

## 获取 API Key

您可以在控制台查看您的 API Key：https://console.volcengine.com/speech/new/setting/apikeys?projectName=default

或者使用 API 接口获取（见下方 ListAPIKeys）。

## 使用方法

在任意接口中，填入 header 即可，不用填写 appid：

```
x-api-key: ${your-api-key}
```

## 禁用或删除

当您发现您的 API Key 可能已经泄露时，可以在控制台上禁用或者删除它，或者调用接口来禁用（删除）它。

---


---

# ListAPIKeys - 拉取APIKey列表--豆包语音-火山引擎

拉取APIKey列表
## 调试
API Explorer您可以通过 API Explorer 在线发起调用，无需关注签名生成过程，快速获取调用结果。[去调试](https://api.volcengine.com/api-explorer/?action=ListAPIKeys&groupName=api_key&serviceCode=speech_saas_prod&version=2025-05-20)
## 请求参数
下方仅列出该接口特有的请求参数和部分公共参数。更多信息请见[公共参数](/docs/6369/67268?lang=zh)。Action string 必选 示例值：ListAPIKeys要执行的操作，取值：ListAPIKeys。Version string 必选 示例值：2025-05-20API的版本，取值：2025-05-20。ProjectName string 必选 示例值：defaultProjectNameOnlyAvailable boolean 可选 示例值：true是否仅可用
## 返回参数
下方仅列出本接口特有的返回参数。更多信息请参见[返回结构](/docs/6369/80336?lang=zh)。APIKeys object[] 示例值：参考响应示例APIKeysDisable booleanDisableCreateTime string 示例值：2025-01-01T00:00:00Z创建时间UpdateTime string 示例值：2025-01-01T00:00:00Z更新时间APIKey string 示例值：xxx-xxx-xxx-xxxAPIKeyName string 示例值：foobarNameID integer 示例值：10IDPageNumber integer 示例值：1PageNumberPageSize integer 示例值：10PageSizeTotalCount integer 示例值：10TotalCountNextToken string 示例值：xxx下一次分页的 tokenMaxResults integer 示例值：100MaxResults
## 请求示例
text复制POST /?Action=ListAPIKeys&Version=2025-05-20 HTTP/1.1Host: https://open.volcengineapi.comContent-Type: application/json; charset=UTF-8X-Date: 20250819T031544ZX-Content-Sha256: 287e874e******d653b44d21eAuthorization: HMAC-SHA256 Credential=Adfks******wekfwe/20250819/cn-beijing/speech_saas_prod/request, SignedHeaders=host;x-content-sha256;x-date, Signature=47a7d934ff7b37c03938******cd7b8278a40a1057690c401e92246a0e41085f{  "ProjectName": "default",  "OnlyAvailable": true}
## 返回示例
json复制{  "ResponseMetadata": {    "RequestId": "20250819111532042225015109363FE4",    "Action": "ListAPIKeys",    "Version": "2025-05-20",    "Service": "speech_saas_prod",    "Region": "cn-beijing"  },  "Result": {    "APIKeys": [      {        "Disable": false,        "CreateTime": "2025-01-01T00:00:00Z",        "UpdateTime": "2025-01-01T00:00:00Z",        "APIKey": "xxx-xxx-xxx-xxx",        "Name": "foobar",        "ID": 10      }    ],    "PageNumber": 1,    "PageSize": 1,    "TotalCount": 713,    "NextToken": "0in9J",    "MaxResults": 100  }}
## 错误码
您可访问[公共错误码](/docs/6369/68677?lang=zh)，获取更多错误码信息。