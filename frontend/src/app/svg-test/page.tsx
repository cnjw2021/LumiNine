import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function SVGTestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-white text-center mb-8 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
          九星盤 SVGダウンロード
        </h1>
        
        <div className="flex justify-center">
          <Link href="/svg-test/kyusei-demo" className="group">
            <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 hover:border-green-500 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-green-500/20 max-w-md">
              <h2 className="text-2xl font-bold text-white mb-4 text-center">九星気学デモ</h2>
              <p className="text-slate-400 mb-6 text-center">
                正確な九星配置とインタラクティブ機能を持つ九星盤。
                高品質なSVGファイルとしてダウンロード可能。
              </p>
              <div className="text-green-400 font-medium group-hover:text-green-300 text-center text-lg">
                メインデモ →
              </div>
              <div className="flex gap-2 mt-6 text-xs justify-center flex-wrap">
                <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded">正確配置版</span>
                <span className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded">使用例</span>
                <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded">インタラクティブ</span>
                <span className="bg-orange-500/20 text-orange-400 px-2 py-1 rounded">SVGダウンロード</span>
              </div>
            </div>
          </Link>
        </div>

        <div className="mt-12 text-center">
          <Link 
            href="/" 
            className="inline-flex items-center px-6 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
          >
            ← メインページに戻る
          </Link>
        </div>
      </div>
    </div>
  );
} 