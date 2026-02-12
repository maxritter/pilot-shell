import { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame, useThree, ThreeEvent } from "@react-three/fiber";
import * as THREE from "three";

const FONT: Record<string, number[][]> = {
  C: [
    [0,1,1,1,1],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [0,1,1,1,1],
  ],
  L: [
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,1,1,1],
  ],
  A: [
    [0,1,1,1,0],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,1,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
  ],
  U: [
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [0,1,1,1,0],
  ],
  D: [
    [1,1,1,1,0],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,1,1,0],
  ],
  E: [
    [1,1,1,1,1],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,1,1,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,1,1,1],
  ],
  P: [
    [1,1,1,1,0],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,1,1,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
    [1,1,0,0,0],
  ],
  I: [
    [1,1,1],
    [0,1,0],
    [0,1,0],
    [0,1,0],
    [0,1,0],
    [0,1,0],
    [1,1,1],
  ],
  O: [
    [0,1,1,1,0],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [1,1,0,1,1],
    [0,1,1,1,0],
  ],
  T: [
    [1,1,1,1,1],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
  ],
};

const CELL = 0.42;
const CUBE = 0.36;
const LINE_GAP = 1.0;
const LETTER_GAP = 1;

interface CubeData {
  targetX: number;
  targetY: number;
}

function computeLinePositions(word: string, offsetY: number): CubeData[] {
  const cubes: CubeData[] = [];

  let totalWidth = 0;
  for (let li = 0; li < word.length; li++) {
    const bitmap = FONT[word[li]];
    if (!bitmap) continue;
    totalWidth += bitmap[0].length * CELL;
    if (li < word.length - 1) totalWidth += LETTER_GAP * CELL;
  }

  let cursorX = -totalWidth / 2;
  for (let li = 0; li < word.length; li++) {
    const bitmap = FONT[word[li]];
    if (!bitmap) continue;
    const rows = bitmap.length;
    const cols = bitmap[0].length;
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        if (bitmap[row][col] === 1) {
          cubes.push({
            targetX: cursorX + col * CELL,
            targetY: offsetY - row * CELL,
          });
        }
      }
    }
    cursorX += cols * CELL + LETTER_GAP * CELL;
  }
  return cubes;
}

const BASE_BLUE = new THREE.Color("#5B9BD5");
const BRIGHT_BLUE = new THREE.Color("#8BB8E8");
const HOVER_BLUE = new THREE.Color("#A8D0F5");
const _tmp = new THREE.Color();

interface CubeState {
  velX: number;
  velY: number;
  velZ: number;
  scattered: boolean;
  returnProgress: number;
}

function VoxelMesh() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const { pointer, viewport } = useThree();
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const [built, setBuilt] = useState(false);
  const buildRef = useRef(0);

  const allCubes = useMemo(() => {
    const lineSpan = 6 * CELL;
    const total = lineSpan + LINE_GAP + lineSpan;
    const topY = total / 2;
    const bottomY = topY - lineSpan - LINE_GAP;
    return [
      ...computeLinePositions("CLAUDE", topY),
      ...computeLinePositions("PILOT", bottomY),
    ];
  }, []);

  const cubeStates = useRef<CubeState[]>(
    allCubes.map(() => ({ velX: 0, velY: 0, velZ: 0, scattered: false, returnProgress: 1 })),
  );
  const displaced = useRef<Float32Array>(new Float32Array(allCubes.length * 3));

  useEffect(() => {
    for (let i = 0; i < allCubes.length; i++) {
      displaced.current[i * 3] = allCubes[i].targetX;
      displaced.current[i * 3 + 1] = allCubes[i].targetY;
      displaced.current[i * 3 + 2] = 0;
    }
  }, [allCubes]);

  const baseColors = useMemo(() => {
    const arr = new Float32Array(allCubes.length * 3);
    const color = new THREE.Color();
    for (let i = 0; i < allCubes.length; i++) {
      color.copy(BASE_BLUE).lerp(BRIGHT_BLUE, Math.random() * 0.5);
      arr[i * 3] = color.r;
      arr[i * 3 + 1] = color.g;
      arr[i * 3 + 2] = color.b;
    }
    return arr;
  }, [allCubes]);

  const colorArray = useMemo(() => new Float32Array(baseColors), [baseColors]);

  useEffect(() => {
    if (!meshRef.current) return;
    meshRef.current.instanceColor = new THREE.InstancedBufferAttribute(colorArray, 3);
  }, [colorArray]);

  useEffect(() => {
    const start = performance.now();
    const duration = 1200;
    let raf: number;
    const tick = () => {
      const p = Math.min((performance.now() - start) / duration, 1);
      buildRef.current = p;
      if (p >= 1) setBuilt(true);
      else raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  const initPositions = useMemo(() => {
    return allCubes.map((c) => ({
      x: c.targetX + (Math.random() - 0.5) * 2,
      y: c.targetY + (Math.random() - 0.5) * 2,
      z: -1.5 + Math.random() * -1,
    }));
  }, [allCubes]);

  const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    const hit = e.point;
    const states = cubeStates.current;
    const disp = displaced.current;
    for (let i = 0; i < allCubes.length; i++) {
      const cx = disp[i * 3];
      const cy = disp[i * 3 + 1];
      const dx = cx - hit.x;
      const dy = cy - hit.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 1.5) {
        const force = (1.5 - dist) / 1.5;
        const angle = Math.atan2(dy, dx);
        states[i].velX = Math.cos(angle) * force * 3;
        states[i].velY = Math.sin(angle) * force * 3;
        states[i].velZ = (Math.random() * 0.5 + 0.5) * force * 2;
        states[i].scattered = true;
        states[i].returnProgress = 0;
      }
    }
  };

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    const time = state.clock.elapsedTime;
    const mouseX = pointer.x * viewport.width * 0.5;
    const mouseY = pointer.y * viewport.height * 0.5;
    const colorAttr = meshRef.current.instanceColor;
    const bp = buildRef.current;
    const states = cubeStates.current;
    const disp = displaced.current;

    for (let i = 0; i < allCubes.length; i++) {
      const cube = allCubes[i];
      const st = states[i];

      let x: number, y: number, z: number, scale: number;

      if (!built) {
        const stagger = Math.min(bp * 1.3 - (i / allCubes.length) * 0.3, 1);
        const t = easeOut(Math.max(0, stagger));
        const init = initPositions[i];
        x = init.x + (cube.targetX - init.x) * t;
        y = init.y + (cube.targetY - init.y) * t;
        z = init.z * (1 - t);
        scale = t;
      } else if (st.scattered) {
        st.returnProgress += delta * 1.5;
        st.velX *= 0.92;
        st.velY *= 0.92;
        st.velZ *= 0.92;

        if (st.returnProgress >= 1) {
          st.scattered = false;
          st.returnProgress = 1;
          disp[i * 3] = cube.targetX;
          disp[i * 3 + 1] = cube.targetY;
          disp[i * 3 + 2] = 0;
        } else {
          disp[i * 3] += st.velX * delta;
          disp[i * 3 + 1] += st.velY * delta;
          disp[i * 3 + 2] += st.velZ * delta;
          const ret = easeOut(st.returnProgress);
          disp[i * 3] += (cube.targetX - disp[i * 3]) * ret * delta * 3;
          disp[i * 3 + 1] += (cube.targetY - disp[i * 3 + 1]) * ret * delta * 3;
          disp[i * 3 + 2] += (0 - disp[i * 3 + 2]) * ret * delta * 3;
        }
        x = disp[i * 3];
        y = disp[i * 3 + 1];
        z = disp[i * 3 + 2];
        scale = 1;
      } else {
        x = cube.targetX;
        y = cube.targetY;
        z = Math.sin(time * 0.6 + cube.targetX * 0.3 + cube.targetY * 0.2) * 0.025;
        disp[i * 3] = x;
        disp[i * 3 + 1] = y;
        disp[i * 3 + 2] = z;
        scale = 1;
      }

      const dx = mouseX - cube.targetX;
      const dy = mouseY - cube.targetY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const proximity = Math.max(0, 1 - dist / 2.5);
      if (built && !st.scattered) {
        z += proximity * 0.08;
      }

      dummy.position.set(x, y, z);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.setScalar(scale);
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);

      if (colorAttr) {
        const hoverT = (built && !st.scattered) ? proximity * 0.35 : 0;
        _tmp.setRGB(baseColors[i * 3], baseColors[i * 3 + 1], baseColors[i * 3 + 2]);
        _tmp.lerp(HOVER_BLUE, hoverT);
        colorAttr.setXYZ(i, _tmp.r, _tmp.g, _tmp.b);
      }
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
    if (colorAttr) colorAttr.needsUpdate = true;
  });

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, allCubes.length]}
      frustumCulled={false}
      onClick={handleClick}
      onPointerDown={handleClick}
    >
      <boxGeometry args={[CUBE, CUBE, CUBE]} />
      <meshStandardMaterial
        color="#ffffff"
        roughness={0.5}
        metalness={0.1}
      />
    </instancedMesh>
  );
}

function Scene() {
  return (
    <>
      {/* High ambient for even base + soft front light for 3D depth */}
      <ambientLight intensity={1.0} />
      <directionalLight position={[0, 1, 10]} intensity={0.5} />
      <VoxelMesh />
    </>
  );
}

const VoxelLogo3D = () => (
  <div
    className="w-[80vw] max-w-[220px] xs:max-w-[270px] sm:max-w-[380px] md:max-w-[460px] lg:max-w-[540px] aspect-[2/1]"
    aria-label="Claude Pilot - Claude Code is powerful. Pilot makes it reliable."
    role="img"
  >
    <Canvas
      camera={{ position: [0, 0, 8], fov: 50 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      style={{ background: "transparent" }}
    >
      <Scene />
    </Canvas>
  </div>
);

export default VoxelLogo3D;
