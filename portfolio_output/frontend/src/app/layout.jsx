// File: app/layout.jsx
import Link from 'next/link';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
        <style dangerouslySetInnerHTML={{__html: `
          :root { --primary: #00f3ff; }
          * { box-sizing: border-box; }
          body {
            margin: 0; padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #030303;
            background-image: 
              radial-gradient(circle at 15% 50%, rgba(20, 20, 20, 0.4), transparent 25%),
              radial-gradient(circle at 85% 30%, rgba(10, 10, 10, 0.4), transparent 25%);
            color: #ededed;
            min-height: 100vh;
          }
          
          /* Navigation */
          .top-nav {
            position: fixed; top: 0; width: 100%; z-index: 1000;
            background: rgba(3, 3, 3, 0.7);
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex; justify-content: space-between; align-items: center;
            padding: 1rem 5vw; height: 70px;
          }
          .brand-logo {
            font-size: 1.35rem; font-weight: 800; color: #fff; text-decoration: none;
            display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.02em;
          }
          .brand-badge {
            font-size: 0.7em; padding: 0.2rem 0.5rem; background: var(--primary); color: #000;
            border-radius: 4px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
          }
          .nav-menu { display: flex; gap: 2rem; }
          .nav-link {
            color: #888; text-decoration: none; font-size: 0.95rem; font-weight: 500;
            transition: all 0.2s; position: relative;
          }
          .nav-link:hover { color: #fff; }
          .nav-link::after {
            content: ''; position: absolute; bottom: -24px; left: 0; width: 100%; height: 2px;
            background: var(--primary); opacity: 0; transition: opacity 0.2s;
          }
          .nav-link:hover::after { opacity: 1; }

          /* Layout Container */
          .page-wrapper {
            max-width: 1200px; margin: 0 auto; padding: 120px 2rem 4rem 2rem;
          }

          /* Headers */
          .page-header { text-align: left; margin-bottom: 4rem; max-width: 800px; }
          .tag-pill {
            display: inline-block; padding: 0.4rem 1rem; border-radius: 50px; font-size: 0.8rem;
            font-weight: 600; margin-bottom: 1.5rem; border: 1px solid;
          }
          .page-title {
            font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin: 0 0 1rem 0;
            letter-spacing: -0.03em; color: #fff;
          }
          .page-subtitle {
            font-size: 1.2rem; color: #888; line-height: 1.6; margin: 0;
          }

          /* Grids & Components */
          .component-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;
          }
          .component-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid;
            border-radius: 16px; padding: 2rem;
            display: flex; flex-direction: column; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            backdrop-filter: blur(10px);
          }
          .component-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.2rem; }
          .component-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
          .component-title { font-size: 1.25rem; font-weight: 700; margin: 0; color: #fff; }
          .component-desc { color: #a0a0a0; font-size: 0.95rem; line-height: 1.6; margin: 0 0 1.5rem 0; flex: 1; }
          .component-content { margin-bottom: 1.5rem; }
          
          /* Buttons */
          .action-btn {
            padding: 0.8rem 1.5rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem;
            font-family: inherit; border: 1px solid; cursor: pointer; transition: all 0.2s;
            margin-top: auto; align-self: flex-start;
          }

          /* Animations */
          .fade-in-up { animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; transform: translateY(20px); }
          @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
        `}} />
      </head>
      <body>
        <nav className="top-nav">
            <Link href="/" className="brand-logo">OrchBuilder <span className="brand-badge">OS</span></Link>
            <div className="nav-menu">
                <Link href="/home" className="nav-link">Home</Link><Link href="/resume" className="nav-link">Resume</Link><Link href="/contact" className="nav-link">Contact</Link><Link href="/dashboard" className="nav-link">Dashboard</Link>
            </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
