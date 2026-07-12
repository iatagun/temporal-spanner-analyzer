'use client';

export default function TruncatedWarning() {
  return (
    <div className="p-3 mb-4 border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-400 text-sm rounded-lg animate-in">
      Sonuçlar kısmi: grafik çok yoğun/büyük olduğu için klik araması bir arama
      bütçesinde durduruldu (veya &quot;Maks Klik&quot; sınırı devreye girdi).
      Aşağıdaki metrikler eksik bir klik kümesine dayanıyor olabilir.
    </div>
  );
}
