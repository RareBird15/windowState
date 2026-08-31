# Pencere Durumu

Mevcut ön plandaki pencerenin durumunu sorgulamanızı sağlayan bir NVDA eklentisi.

## Sorun

NVDA, başlığı sorguladığınızda pencerenin ekranı kapladığını, geri yüklendiğini veya ekranın bir kenarına yerleştirildiğini size söylemez. Bu bilgi şu nedenlerden dolayı faydalıdır:

- Bir pencerenin ekranı kaplaması için Windows+Yukarı Ok tuşlarına basmak, bunun yerine Windows 11’in yan yana yerleştirme düzeni seçicisini tetikleyebilir ve pencereyi bilinmeyen bir durumda bırakabilir.
- Gören kullanıcılar, bir pencereye göz atarak onun boyutunu ve konumunu görebilirler. Görme engelli kullanıcılar ise, pencerenin boyutunu değiştirmeyi denemeden veya NVDA’nın pencere durumunu seslendirmesini dinlemeden bunu kontrol etmenin bir yolu yoktur.
- JAWS, bu bilgiyi JAWS+T başlık duyurusunda içerir. NVDA'da böyle bir şey yok.

## Bu Eklentinin İşlevi

1. **NVDA+Shift+T**: Ön plandaki pencerenin durumunu seslendirir. Olası durumlar:
   - Ekranı kaplamış
   - Geri yüklendi (normal pencereli mod)
   - Simge durumuna küçültülmüş
   - Sola yerleştirildi, sağa yerleştirildi, üste yerleştirildi, alta yerleştirildi (yarım ekran yerleşimleri)
   - Sol üst çeyrek, sağ üst çeyrek, sol alt çeyrek, sağ alt çeyrek
   - Not resizable (for windows like the Desktop that can't be maximized or restored)

2. **İsteğe bağlı: NVDA+T geliştirmesi**: Ayarlarda etkinleştirildiğinde, NVDA+T tuşlarına basıldığında pencere başlığı ve ardından durumu sesli olarak duyurulur; örneğin, "Firefox, tam ekran." Bu, JAWS'ın davranışına uygundur. Başlığı hecelemek için NVDA+T tuşlarına iki kez basma ve panoya kopyalamak için üç kez basma işlemleri bu ayardan etkilenmez.

## Ayarlar

Yapılandırmak için NVDA Menüsü, Tercihler, Ayarlar > Pencere Durumu'nu açın:

- **NVDA+T başlığı seslendir seçeneğine pencere durumunu ekle**: Bu seçenek işaretlendiğinde, NVDA+T başlığı seslendirmenin ardından pencere durumunu da ekler. Varsayılan olarak kapalıdır.

Tüm komutlar, NVDA'nın Girdi Hareketleri iletişim kutusunda "Pencere Durumu" kategorisi altında yeniden eşlenebilir.

## Gereksinimler

- NVDA 2026.1 veya sonrası

## Yazar

Lanie Carmelo-Molinar
https://lanie.work

## Lisans

GPL v2
