# Kakao APIs for a weekly notice to a KakaoTalk group chat

Research date: 2026-10-22. Sources are developers.kakao.com, Kakao Business docs, and the Kakao customer center. Some claims cite staff answers on devtalk.kakao.com, the official Kakao developer forum. Each such claim says so.

## Summary

1. No public Kakao API posts into an existing group chat or open chat room. Kakao staff confirmed this in July and August 2026.
2. Channel messages, alimtalk, and brand messages go only 1:1 to channel friends or phone numbers. They need a business channel, and alimtalk and brand messages go through a paid dealer.
3. The Messaging API "send to me" posts to the owner's own chat (나와의 채팅방). It is free and unlimited, and needs no review for app members.
4. Only Kakao Share reaches a group chat. A person must tap it in the KakaoTalk app and pick the room. No REST API or server path exists.
5. Cheapest honest shape: the pipeline calls "send to me" with the link. The owner then forwards it, or taps a Kakao Share button, into the group chat.

## 1. KakaoTalk Channel API (the given link)

- The REST API page has six APIs. None sends a message. APIs 1 and 2 check the channel relationship (`GET /v2/api/talk/channels`, `GET /v2/api/talk/channels/multi`). APIs 3 to 6 manage customer files (고객파일). Source: https://developers.kakao.com/docs/en/kakaotalk-channel/rest-api
- A customer file holds only users who added the channel as a friend: "You can only add the users who have added your Kakao Talk Channel as a friend to the customer file." Source: https://developers.kakao.com/docs/en/kakaotalk-channel/rest-api
- The customer management APIs need a "Customer management API policy agreement". Source: https://developers.kakao.com/docs/en/kakaotalk-channel/rest-api
- The overview page says you send targeted messages from the Partner Center (파트너센터) web UI, with the customer file: "조건별 친구 그룹을 만들어 세분화된 타깃 메시지를 발송할 수 있습니다." The developer docs give no send API for channel messages. Source: https://developers.kakao.com/docs/ko/kakaotalk-channel/common
- "Channel chat" links a user to a 1:1 chat with the channel. Source: https://developers.kakao.com/docs/ko/kakaotalk-channel/common
- "카카오톡 채널은 같은 사업자가 소유한 앱만 연결 가능합니다." Only an app of the same business owner can link to a channel. The business channel review takes about 3 to 5 business days, at https://center-pf.kakao.com. Source: https://developers.kakao.com/docs/ko/kakaotalk-channel/common
- Channel messages (채널 메시지) go to channel friends, to all friends or to a target group. The page does not describe an API. You write and send them in the Partner Center UI. Source: https://kakaobusiness.gitbook.io/main/channel/run/message
- No Channel doc reads mentions group chats or open chat rooms as a target.
- Answer: a channel sends only to its own friends, 1:1, in the channel's chat with each user. No message kind reaches a group chat. Alimtalk and brand messages need a business channel and a template or policy review. See section 5.

## 2. KakaoTalk Messaging API (`talk_message`)

- Send to me: `POST https://kapi.kakao.com/v2/api/talk/memo/default/send`, `.../v2/api/talk/memo/send` (custom template), and `.../v2/api/talk/memo/scrap/send`. The message goes to the user's own chat (나와의 채팅방). "이 기능으로는 다른 사용자에게 메시지를 보낼 수 없고." You cannot send to other users with this feature. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Send to friends: `POST https://kapi.kakao.com/v1/api/talk/friends/message/default/send`, `.../message/send`, and `.../message/scrap/send`. Recipients are friend `uuid` values. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Friend send limit per request: "한 번에 최대 5명의 친구에게 메시지를 보낼 수 있습니다." Five friends at most per call. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Friend send needs the KakaoTalk Social permission: "카카오톡 소셜 API 사용 권한이 있어야 친구에게 메시지 발송 기능을 사용할 수 있습니다." Source: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Scope: "카카오톡 메시지 API는 같은 서비스 내 사용자간 메시지 발송만 지원합니다." Messages go only between users of the same service. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/common
- Friend consent: a friend shows in the friend list or picker only if all four conditions hold. The friend is linked to the app. The friend agreed to the "카카오 서비스 내 친구 목록 제공" item. The friend is not hidden or blocked. The friend's profile is public. Source: https://developers.kakao.com/docs/ko/kakaotalk-social/common
- So each league member must log in to the app once with Kakao Login. Each must also agree to the friends item and keep a public profile.
- Group chat: the Messaging docs do not mention group chats. A Kakao staff answer on 2026-08-05 says: "카카오톡 메시지 API 기능은 이용자간 메시징 기능으로 채팅방을 대상으로 메시지를 보내는 기능은 아닙니다." The Message API sends between users, not to a chat room. Source (official forum, staff): https://devtalk.kakao.com/t/api/151008
- Daily limits, before the permission review: send to me has no limit. Send to friends has 30 per day. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/common
- Daily limits, after the review: send to me has no limit. Send to friends has 30,000 per app per day. The extra caps are 100 per sender, 100 per recipient, and 20 per sender and recipient pair. Sources: https://developers.kakao.com/docs/ko/kakaotalk-message/common and https://developers.kakao.com/docs/ko/getting-started/quota
- Error -532 means "daily message limit per sender has been exceeded". Source: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Tokens: the REST API access token lasts 6 hours. The refresh token lasts 2 months. You can renew it when one month or less remains. Each renewal gives a new refresh token and voids the old one. A weekly job must store the newest refresh token. Source: https://developers.kakao.com/docs/ko/kakaologin/common

## 3. Open chat and group chats

- No public Developers doc gives an API that posts into an existing group chat.
- A page titled "카카오톡 오픈채팅 타입" exists at https://developers.kakao.com/docs/in/kakaotalk-openlink/common. A search snippet says it links a service app to open chats and sends messages to open chat links that the API creates. The page needs a Kakao login, so I could not read it. The `/docs/in/` path is not in the public `/docs/ko/` or `/docs/en/` trees. It looks like a gated partner doc.
- Kakao staff deny a public open chat API. On 2026-07-23: "현재 오픈채팅 관련 API는 제공하고 있지 않는점 참고 부탁드립니다." Source (official forum, staff): https://devtalk.kakao.com/t/api-api/150798
- On 2025-01-03: "아쉽지만, 디벨로퍼스에서는 오픈채팅 관련 API를 제공하지 않습니다." The same answer points to customer service feedback or a partnership proposal. Source (official forum, staff): https://devtalk.kakao.com/t/webhook-api/141656
- On 2026-08-05, staff said that sending to an existing group chat (단체방) or open chat is not offered. Source (official forum, staff): https://devtalk.kakao.com/t/api/151008
- Search snippets cite a staff line that Kakao has an official open chat bot only and does not support user bots. I did not open that thread. Source (search result only): https://devtalk.kakao.com/t/topic/137269
- Answer: deny. No public API or bot API posts into a group chat or open chat room.

## 4. Kakao Share (카카오톡 공유)

- The user picks content in the service and shares it to friends or chat rooms: "사용자가 직접 서비스에서 콘텐츠를 선택해 사용자의 카카오톡 친구나 대화방으로 공유하는 기능입니다." The user picks the target in KakaoTalk, and the send happens after that pick. Source: https://developers.kakao.com/docs/ko/kakaotalk-share/common
- Group chat: this is the one feature that can put a message in a group chat. With the picker type `chat`, "그룹 채팅방은 최대 5개까지만 선택 가능". The picker setting needs a permission, KakaoTalk 26.2.0 or later, and JavaScript SDK 2.8.0 or later. Source: https://developers.kakao.com/docs/ko/kakaotalk-share/common
- Server-side: "REST API 방식은 지원하지 않습니다." No REST API. The share must start from a client SDK: JavaScript, Android, iOS, or Flutter. Source: https://developers.kakao.com/docs/ko/kakaotalk-share/common
- The JavaScript `sendDefault` call needs a registered "JavaScript SDK 도메인". The send happens inside KakaoTalk: "카카오톡 공유는 사용자가 카카오톡에서 메시지를 전송하므로". Source: https://developers.kakao.com/docs/ko/kakaotalk-share/js-link
- Mac without the app: the docs do not describe this. A 2016 forum reply says a share works only from a mobile device. The reply is old, and the page does not mark the author as staff. Source: https://devtalk.kakao.com/t/pc-pc/27170
- A webhook can report a successful share. Source: https://developers.kakao.com/docs/ko/kakaotalk-share/common
- Limits: 30,000 calls per day free. Past the free quota, Kakao Share costs 50 KRW per call. A promotional price of 10 KRW per call applies. See section 5. Source: https://developers.kakao.com/docs/ko/getting-started/quota

## 5. Cost and gates

### Channel side

- Channel messages: 15 KRW for a general message and 20 KRW for a target message, VAT excluded. You need a BizWallet with charged cash: "메시지를 발송하기 위해서는 비즈월렛과 캐시 충전이 필요합니다." You send in the Partner Center UI. Source: https://kakaobusiness.gitbook.io/main/channel/run/message
- Alimtalk (알림톡): informational messages only, with templates that Kakao approves. It goes to phone numbers, also to users who did not add the channel. It needs a business channel with 홈공개 on and service contact info. Source: https://kakaobusiness.gitbook.io/main/ad/infotalk
- Alimtalk dealer rule: "알림톡은 기술적인 지원이 필요한 API상품으로 공식 딜러사를 통해서만 진행이 가능합니다." Only official dealers sell it. Each dealer sets its own price: "각 사의 서비스 제공 범위/ 발송 단가/ 연동 방법 등의 계약조건이 다를 수 있음". Source: https://cs.kakao.com/helps_html/1073208551?locale=ko
- Template review for alimtalk takes about 2 business days, per the customer center. Source (search result only): https://cs.kakao.com/helps_html/1073194762?locale=ko
- Brand message (브랜드 메시지): personalized ad messages through an API, to channel friends and users who agreed to ads. It goes through official dealers and needs a business channel. Ads must show "(광고)" and an opt-out. The page gives no price. Source: https://kakaobusiness.gitbook.io/main/ad/brandmessage
- Friendtalk (친구톡): no Kakao page I read uses this name. The docs I read do not say if brand message replaces it.

### Messaging API side

- The quota page lists no price for KakaoTalk message sends. Send to me has no count limit. Sources: https://developers.kakao.com/docs/ko/getting-started/quota and https://developers.kakao.com/docs/ko/kakaotalk-message/common
- The paid API settings page lists only Kakao Share and Kakao Map as paid APIs. Paid use starts after the free quota, with a BizWallet and an auto-pay card. Source: https://developers.kakao.com/docs/ko/app-setting/paid-api
- The monthly quota for all APIs is 3,000,000 calls. Source: https://developers.kakao.com/docs/ko/getting-started/quota
- Kakao Share price: 50 KRW per call past the free quota. The quota page says 10 KRW per call from 2026-02-02 to 2027-12-31. A search summary of the same page gave 2026-12-31. Source: https://developers.kakao.com/docs/ko/getting-started/quota
- A weekly notice to one group is far below every free quota.

## 6. App registration for an individual

- Create one app per service in the Kakao Developers console. The REST API key is under 앱 > 플랫폼 키 > REST API 키. Client secret is on by default, so token requests must send `client_secret`. Source: https://developers.kakao.com/docs/ko/app-setting/app
- Kakao Login needs a registered redirect URI. You can register up to 10. The `redirect_uri` value must match exactly, or you get `KOE006`. Source: https://developers.kakao.com/docs/ko/app-setting/app
- The `talk_message` item cannot be "required". It can be optional or in-use, with "제한된 기능 제공, 사용 권한 신청". Before the permission, the feature works only for app members or under quota limits. The `friends` item has the same rule. Source: https://developers.kakao.com/docs/ko/kakaologin/utilize
- Tests before approval run with app members: "앱 멤버를 대상으로 기능 동작 여부를 확인합니다." The owner is an app member, so "send to me" works for him without a review. Source: https://developers.kakao.com/docs/ko/kakaotalk-message/common
- The friend send permission has four steps: "비즈 앱 전환", "신청 자격 확인", "비즈니스 정보 심사", then "추가 기능 신청". Source: https://developers.kakao.com/docs/ko/kakaotalk-message/common
- The friend list permission needs a service URL or app link and a screenshot of the live feature. It also needs a reason and a use scenario. The review takes 3 to 5 business days. Source: https://developers.kakao.com/docs/ko/kakaotalk-social/common
- An individual without a business number can make a "개인 개발자 비즈 앱". The owner must pass identity check and agree to the Kakao Business terms. This app type "사업자 정보가 없어" cannot link a business channel. Source: https://developers.kakao.com/docs/ko/app-setting/app
- So an individual can apply for friend send. He cannot link a business channel, so alimtalk and brand messages are closed to him.

## Open questions

1. Does the business info review (비즈니스 정보 심사) accept a personal league site for friend send? The docs give no rule for individuals. Forum posts report some denials.
2. What does the gated open chat page say? It is at https://developers.kakao.com/docs/in/kakaotalk-openlink/common and needs a login. Staff on the public forum say no open chat API exists, so it is likely partner-only.
3. Can Kakao Share run from a Mac browser with KakaoTalk for Mac? The docs do not say. The only answer is a 2016 forum reply.
4. Does "send to me" need the `talk_message` permission review, or only the consent item? The docs suggest app members can use it before the review, but they do not say it outright.
5. The end date of the 10 KRW Kakao Share promotion: 2026-12-31 or 2027-12-31. This does not matter at one share per week.
6. Fetch failures: https://developers.kakao.com/docs/ko/getting-started/paid-api and https://developers.kakao.com/docs/ko/getting-started/app returned 404. The `app-setting` paths replaced them.

## Sources

- https://developers.kakao.com/docs/en/kakaotalk-channel/rest-api
- https://developers.kakao.com/docs/ko/kakaotalk-channel/common
- https://developers.kakao.com/docs/ko/kakaotalk-message/common
- https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- https://developers.kakao.com/docs/ko/kakaotalk-social/common
- https://developers.kakao.com/docs/ko/kakaotalk-share/common
- https://developers.kakao.com/docs/ko/kakaotalk-share/js-link
- https://developers.kakao.com/docs/ko/getting-started/quota
- https://developers.kakao.com/docs/ko/app-setting/paid-api
- https://developers.kakao.com/docs/ko/app-setting/app
- https://developers.kakao.com/docs/ko/kakaologin/utilize
- https://developers.kakao.com/docs/ko/kakaologin/common
- https://developers.kakao.com/docs/in/kakaotalk-openlink/common (login wall, not read)
- https://kakaobusiness.gitbook.io/main/channel/run/message
- https://kakaobusiness.gitbook.io/main/ad/brandmessage
- https://kakaobusiness.gitbook.io/main/ad/infotalk
- https://cs.kakao.com/helps_html/1073208551?locale=ko
- https://cs.kakao.com/helps_html/1073194762?locale=ko (search result only)
- https://devtalk.kakao.com/t/api/151008 (official forum, staff answer)
- https://devtalk.kakao.com/t/api-api/150798 (official forum, staff answer)
- https://devtalk.kakao.com/t/webhook-api/141656 (official forum, staff answer)
- https://devtalk.kakao.com/t/topic/137269 (search result only)
- https://devtalk.kakao.com/t/pc-pc/27170 (official forum, 2016 reply)

## Decision 2026-10-22

Parked. No Kakao API reaches the group chat. Every shape ends with a forward or a paste by hand. Brian chose to pass. If this comes back, the cheapest shape is a ready message in the publish output, no Kakao app.
