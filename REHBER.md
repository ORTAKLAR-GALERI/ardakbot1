# Discord Moderasyon Botu Kullanım Kılavuzu

Bu kılavuz, sunucu yetkililerinin moderasyon botunu yönetmesi için geliştirilmiş komut listesini içerir. Aşağıdaki komutları herhangi bir metin kanalından kullanarak hedeflenen kişilere işlem uygulayabilirsiniz.

| Komut | Açıklama / Yaptığı İşlem |
| :--- | :--- |
| **`.end ID`** | Hedef kullanıcının yazdığı metin mesajlarını otomatik olarak siler. Ayrıca kullanıcı sesli bir kanala bağlanmak istediğinde sağır/dilsiz (mute & deafen) yapıp anında kanaldan atar. |
| **`.ses ID`** | Hedef kullanıcının metin mesajlarına müdahale etmez. Ancak sesli bir kanala bağlanmak istediğinde sağır/dilsiz (mute & deafen) yapıp anında kanaldan atar. |
| **`.kulak ID`** | Hedef kullanıcının ses kanalında kalmasına izin verir ancak sunucu tarafından kalıcı olarak sağır/dilsiz (mute & deafen) olmasını sağlar. Kişi hoparlör veya mikrofon kilidini kaldırmaya çalışırsa sistem tekrar kapatır. |
| **`.chat ID`** | Hedef kullanıcının ses kanallarına bağlanmasına engel olmaz. Ancak yazılı metin kanallarına gönderdiği tüm sohbet mesajlarının bot tarafından otomatik olarak anında silinmesini sağlar. |
| **`.mal ID`** | Hedef kullanıcıya herhangi bir sohbet veya ses kısıtlaması getirmez. Kullanıcının metin kanallarında gönderdiği her mesajın altına bot tarafından 🇲, 🇦, 🇱 harf emojilerinin tepki (reaction) olarak atılmasını sağlar. |
| **`.liste`** | Veri tabanında o an cezası aktif olarak devam eden tüm kullanıcıların ID'lerini ve uygulanan ceza türlerini listeler. |
| **`.cikar ID`** | Hedef kullanıcının sistemdeki tüm cezalarını veri tabanından anında siler. Kişi o an kalıcı bir ses engeli altındaysa (Örn: kulaklık/mikrofon kapanması) bu izinlerini anında geri verip normale dönmesini sağlar. |

**Önemli Not:** Komutların çalışması için etiket atmak (`@kullanici`) yerine hedef kişinin doğrudan rakamlardan oluşan Discord Kullanıcı Kımliğini (ID) kullanmalısınız. 
*(Örnek Geçerli Kullanım: `.ses 123456789012345678`)*
