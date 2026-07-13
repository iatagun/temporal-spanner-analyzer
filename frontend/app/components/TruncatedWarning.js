'use client';

export default function TruncatedWarning() {
  return (
    <div className="p-3 mb-4 border border-[var(--color-warning-border)] bg-[var(--color-warning-bg)] text-[var(--color-warning)] text-sm rounded-lg animate-in">
      Sonuçlar kısmi: grafik çok yoğun/büyük olduğu için klik araması bir arama
      bütçesinde durduruldu (veya &quot;Maks Klik&quot; sınırı devreye girdi).
      Aşağıdaki metrikler eksik bir klik kümesine dayanıyor olabilir.
    </div>
  );
}
