'use client';

export default function Header() {
  return (
    <header className="mb-8 pb-6 border-b border-border">
      <h1 className="text-xl font-semibold tracking-tight text-gray-900">
        Temporal Spanner Analyzer
      </h1>
      <p className="text-sm text-gray-500 mt-1.5 max-w-2xl leading-relaxed">
        Derlem dilbiliminde kavramlarin zamansal evrimini analiz eden bir arac.
        Baligacs (2026) &quot;Temporal Cliques Admit Linear Spanners&quot; makalesindeki
        lineer spanner algoritmasini kullanarak, buyuk derlemlerdeki kelime
        birlikteliklerini seyrek zamanli cizgelere indirger; kavram kumelerinin
        dogum, buyume ve kaybolus sureclerini gorunur kilar.
      </p>
      <div className="flex gap-3 mt-3 text-xs text-gray-400">
        <span>Girdi: CSV, JSON, CoNLL-U, VRT</span>
        <span aria-hidden="true">&middot;</span>
        <span>Cikti: Spanner cizgeler, trend grafikleri, karsilastirma, kesif</span>
      </div>
    </header>
  );
}
