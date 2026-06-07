# GLOSA 3D Simulýasiýa
**Green Light Optimal Speed Advisory**  
Şanazar Sarjaýew | TDU 2026

---

## 📥 EXE Göçürip almak

1. Ýokardaky **Actions** goýmasyna giriň
2. Iň soňky **Build EXE** işini açyň
3. **Artifacts** bölüminden `GLOSA_3D_Sim_EXE` göçürip alyň

## 🚀 Özüňiz gurmak

```bash
pip install pygame numpy pyinstaller
pyinstaller --onefile --noconsole --name "GLOSA_3D_Sim" glosa_3d_sim.py
```
`dist/GLOSA_3D_Sim.exe` faýly döreýär.

## 🎮 Dolandyryş

| Düwme | Hereket |
|-------|---------|
| `SPACE` | Başla / Sakla / Täzele |
| `G` | GLOSA açyk/ýapyk |
| `C` | Kamera öňe/yza |
| `1` | Açyk howa |
| `2` | Ýagyş |
| `3` | Gar |
| `4` | Duman |
| `R` | Täzele |
| `ESC` | Çyk |

## 📦 Gerekli kitaphanalar

- `pygame`
- `numpy`
