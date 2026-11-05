'use client';

import * as React from 'react';
import { ArrowRight } from 'lucide-react';
import { GlassButton } from '@/components/glass';

const STOPS = ['Resume', 'Skill gaps', 'Roadmap', 'Assessment', 'Job matches', 'Tailoring'];
const FACTS = [
  { big: '6', small: 'steps, one profile' },
  { big: '~1 min', small: 'to read your resume' },
  { big: 'PDF · DOCX', small: 'accepted' },
];

/**
 * Landing hero: a lavender path walks over a dot terrain through the six CoachPath steps.
 * three.js loads only on this page (dynamic import). Without WebGL the gradient fallback shows;
 * under reduced motion the path is drawn complete and nothing moves.
 */
export function PathHero() {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const labelRefs = React.useRef<(HTMLDivElement | null)[]>([]);
  const pausedRef = React.useRef(false);
  const [paused, setPaused] = React.useState(false);
  const [hasGL, setHasGL] = React.useState(true);

  React.useEffect(() => {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    pausedRef.current = reduce;
    setPaused(reduce);

    let raf = 0;
    let cleanup = () => {};
    let cancelled = false;

    import('three').then((THREE) => {
      const canvas = canvasRef.current;
      if (cancelled || !canvas) return;
      let renderer: InstanceType<typeof THREE.WebGLRenderer>;
      try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
      } catch {
        setHasGL(false);
        return;
      }
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      const scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0x000000, 0.035);
      const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);

      // Dot terrain of gentle hills.
      const hill = (x: number, z: number) =>
        Math.sin(x * 0.35) * 0.6 + Math.cos(z * 0.3 + x * 0.1) * 0.5 + Math.sin((x + z) * 0.15) * 0.4;
      const N = 120, size = 52, pts: number[] = [];
      for (let i = 0; i < N; i++)
        for (let j = 0; j < N; j++) {
          const x = (i / (N - 1) - 0.5) * size, z = (j / (N - 1) - 0.5) * size;
          pts.push(x, hill(x, z) - 1.6, z);
        }
      const dotGeo = new THREE.BufferGeometry();
      dotGeo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      scene.add(new THREE.Points(dotGeo, new THREE.PointsMaterial({ color: 0x3f3560, size: 0.07, sizeAttenuation: true })));

      // The path rides above the terrain through six stops.
      const stopXZ = [[2.5, 6.5], [7, 3.8], [2.5, 0.4], [7.5, -3], [3, -6.4], [7.5, -9.6]];
      const ctrl = [[0, 11], ...stopXZ, [4, -15]].map(([x, z]) => new THREE.Vector3(x, hill(x, z) - 1.2, z));
      const curve = new THREE.CatmullRomCurve3(ctrl, false, 'catmullrom', 0.5);
      const tube = new THREE.TubeGeometry(curve, 400, 0.05, 8, false);
      const total = tube.index!.count;
      tube.setDrawRange(0, 0);
      scene.add(new THREE.Mesh(tube, new THREE.MeshBasicMaterial({ color: 0xc4b5fd })));
      scene.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 400, 0.02, 6, false), new THREE.MeshBasicMaterial({ color: 0x2a2142 })));

      const stopT = stopXZ.map((_, i) => (i + 1) / (ctrl.length - 1));
      const markers = stopT.map((t) => {
        const g = new THREE.Group();
        g.position.copy(curve.getPointAt(t));
        const core = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), new THREE.MeshBasicMaterial({ color: 0x5b556e }));
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xc4b5fd, transparent: true, opacity: 0, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(new THREE.RingGeometry(0.28, 0.32, 48), ringMat);
        ring.rotation.x = -Math.PI / 2;
        const beamMat = new THREE.MeshBasicMaterial({ color: 0xc4b5fd, transparent: true, opacity: 0 });
        const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.4, 6), beamMat);
        beam.position.y = 0.7;
        g.add(core, ring, beam);
        scene.add(g);
        return { g, core: core.material as InstanceType<typeof THREE.MeshBasicMaterial>, ring, ringMat, beamMat };
      });
      const walker = new THREE.Mesh(new THREE.SphereGeometry(0.11, 24, 16), new THREE.MeshBasicMaterial({ color: 0xc6f432 }));
      scene.add(walker);

      const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
      const onMove = (e: PointerEvent) => {
        mouse.tx = e.clientX / innerWidth - 0.5;
        mouse.ty = e.clientY / innerHeight - 0.5;
      };
      const resize = () => {
        const w = canvas.clientWidth, h = canvas.clientHeight;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        // Desktop: render a wider view and show its left part, so the path sits right of the headline.
        if (w >= 720) camera.setViewOffset(w * 1.5, h, 0, 0, w, h);
        else camera.clearViewOffset();
        camera.updateProjectionMatrix();
      };
      addEventListener('pointermove', onMove, { passive: true });
      addEventListener('resize', resize);
      resize();

      const CYCLE = 16;
      const v = new THREE.Vector3();
      let t0 = performance.now();
      let elapsed = reduce ? CYCLE * 0.999 : 0;
      let visible = true;
      const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
      io.observe(canvas);

      const frame = (now: number) => {
        const dt = Math.min((now - t0) / 1000, 0.05);
        t0 = now;
        if (!visible) { raf = requestAnimationFrame(frame); return; }
        if (!pausedRef.current) elapsed = (elapsed + dt) % (CYCLE + 2);
        const ease = 1 - Math.pow(1 - Math.min(elapsed / CYCLE, 1), 1.6);
        tube.setDrawRange(0, Math.floor((total * ease) / 3) * 3);
        walker.position.copy(curve.getPointAt(Math.max(ease, 0.0001)));

        const narrow = innerWidth < 720;
        mouse.x += (mouse.tx - mouse.x) * 0.04;
        mouse.y += (mouse.ty - mouse.y) * 0.04;
        const drift = pausedRef.current ? 0 : Math.sin(now / 9000) * 0.6;
        camera.position.set(4 + mouse.x * 2 + drift, 9.5 - mouse.y, narrow ? 19 : 14);
        camera.lookAt(4.6, -1.5, -2.5);

        markers.forEach((m, i) => {
          const reached = ease >= stopT[i] - 0.002;
          const near = Math.abs(ease - stopT[i]) < 0.06;
          m.core.color.set(reached ? (near ? 0xddd3ff : 0xc6f432) : 0x5b556e);
          m.ringMat.opacity += ((near ? 0.9 : reached ? 0.25 : 0) - m.ringMat.opacity) * 0.12;
          m.beamMat.opacity += ((near ? 0.7 : 0) - m.beamMat.opacity) * 0.12;
          m.ring.scale.setScalar(near && !pausedRef.current ? 1 + Math.sin(now / 180) * 0.08 : 1);
          const L = labelRefs.current[i];
          if (!L) return;
          v.copy(m.g.position);
          v.y += 0.3;
          v.project(camera);
          const x = (v.x * 0.5 + 0.5) * canvas.clientWidth, y = (-v.y * 0.5 + 0.5) * canvas.clientHeight;
          L.style.transform = `translate(${x}px,${y}px) translate(-50%,-150%)`;
          L.dataset.state = near ? 'on' : reached ? 'done' : '';
          L.style.opacity = v.z < 1 && x > (narrow ? 0 : canvas.clientWidth * 0.5) && x < canvas.clientWidth - 60 ? '1' : '0';
        });
        renderer.render(scene, camera);
        raf = requestAnimationFrame(frame);
      };
      raf = requestAnimationFrame(frame);

      cleanup = () => {
        cancelAnimationFrame(raf);
        removeEventListener('pointermove', onMove);
        removeEventListener('resize', resize);
        io.disconnect();
        scene.traverse((o) => {
          const mesh = o as InstanceType<typeof THREE.Mesh>;
          mesh.geometry?.dispose();
          const mat = mesh.material as { dispose?: () => void } | undefined;
          mat?.dispose?.();
        });
        renderer.dispose();
      };
    });

    return () => {
      cancelled = true;
      cleanup();
    };
  }, []);

  const togglePause = () => {
    pausedRef.current = !pausedRef.current;
    setPaused(pausedRef.current);
  };

  return (
    <section aria-label="Introduction" className="relative isolate flex min-h-[calc(100svh-4rem)] items-end overflow-hidden">
      {/* Fallback ground, also what shows before WebGL starts */}
      <div
        aria-hidden
        className="absolute inset-0 -z-30"
        style={{
          background:
            'radial-gradient(55% 50% at 72% 50%, rgba(124,58,237,.30), transparent 70%), radial-gradient(30% 30% at 86% 28%, rgba(198,244,50,.08), transparent 70%), #000',
        }}
      />
      {hasGL && <canvas ref={canvasRef} aria-hidden className="absolute inset-0 -z-20 block h-full w-full" />}
      {/* Scrim keeps the headline readable over the scene */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[linear-gradient(0deg,#000_0%,rgba(0,0,0,.78)_45%,rgba(0,0,0,0)_80%)] md:bg-[linear-gradient(90deg,rgba(0,0,0,.9)_0%,rgba(0,0,0,.5)_38%,rgba(0,0,0,0)_62%),linear-gradient(0deg,#000_0%,rgba(0,0,0,0)_30%)]"
      />
      <div aria-hidden className="pointer-events-none absolute inset-0 hidden md:block">
        {STOPS.map((name, i) => (
          <div
            key={name}
            ref={(el) => {
              labelRefs.current[i] = el;
            }}
            className="liquid-glass group absolute left-0 top-0 flex items-center gap-2 whitespace-nowrap rounded-full py-1.5 pl-3 pr-3.5 text-[13px] text-ink-muted opacity-0 transition-[color,opacity] duration-300 will-change-transform data-[state=on]:text-ink-fg"
          >
            <i className="h-2 w-2 rounded-full bg-ink-dim transition-colors group-data-[state=done]:bg-lime group-data-[state=on]:bg-lav group-data-[state=on]:shadow-[0_0_0_4px_rgba(196,181,253,.22)]" />
            {name}
          </div>
        ))}
      </div>

      <div className="mx-auto w-full max-w-7xl px-4 pb-20 pt-24 sm:px-6 md:pb-28 lg:px-8">
        <h1 className="max-w-[11ch] font-display text-[clamp(46px,6.6vw,92px)] font-semibold leading-[0.98] tracking-[-0.045em] text-ink-fg">
          One clear path to your <span className="text-lav">next role.</span>
        </h1>
        <p className="mt-6 max-w-[46ch] text-lg leading-relaxed text-ink-muted">
          Upload your resume once. CoachPath finds your skill gaps, builds a learning roadmap, matches you to jobs and tailors
          your resume for each one.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <GlassButton size="lg" href="/signup">
            Build your career profile <ArrowRight className="h-4 w-4" />
          </GlassButton>
          <GlassButton size="lg" variant="glass" href="/how-it-works">
            See how it works
          </GlassButton>
        </div>
        <ul className="mt-10 flex flex-wrap gap-3">
          {FACTS.map((f) => (
            <li key={f.big} className="liquid-glass rounded-2xl px-4 py-3 text-[13px] leading-snug text-ink-muted">
              <b className="block font-mono text-xl font-medium text-ink-fg">{f.big}</b>
              {f.small}
            </li>
          ))}
        </ul>
      </div>

      {hasGL && (
        <button
          type="button"
          onClick={togglePause}
          aria-pressed={paused}
          className="liquid-glass absolute bottom-4 right-4 z-10 h-10 rounded-full px-4 text-[13px] font-medium text-ink-muted transition-colors hover:text-ink-fg sm:right-6 md:bottom-6"
        >
          {paused ? 'Play motion' : 'Pause motion'}
        </button>
      )}
    </section>
  );
}
