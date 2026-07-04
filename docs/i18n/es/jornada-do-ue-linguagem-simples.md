<!-- sync: 196ae2dd -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/jornada-do-ue-linguagem-simples.md`](../../jornada-do-ue-linguagem-simples.md). Todos los idiomas: [INDEX](INDEX.md).

# El Viaje del UE en lenguaje simple

> Guía de bolsillo para abrir al lado mientras haces clic en el **Viaje del UE**
> (en el panel: **Topología → botón "Viaje del UE"**). Cada pantalla del viaje es una
> línea aquí abajo — **sin palabras raras**. Los nombres técnicos aparecen solo entre
> paréntesis, para que reconozcas lo que está en la pantalla.

## La idea en una frase

Un celular entrando en la red es como **una persona llegando a un edificio**: llega,
se identifica, pasa por seguridad, recibe la **llave de una habitación** y una
**dirección**, y entonces puede **enviar y recibir correspondencia**. Es solo eso — el resto
son detalles de "quién hace qué".

---

## Proyecto 2 (OAI + RIC) — las 16 pantallas

| En la pantalla aparece | Qué está pasando (simple) |
|---|---|
| **1. El celular se enciende** | La persona llega a la puerta del edificio. El celular despierta y va a intentar entrar en la red. |
| **2. Radio — conexión física** | Ella se acerca a la recepción. Es el contacto físico (la "radio") entre el celular y la antena. |
| **3. gNB ↔ Core — control** | La recepción (antena) llama a la administración del edificio (el núcleo de la red): "llegó alguien". |
| **4. Registro del UE** | La persona se presenta: "soy fulano, quiero entrar". |
| **5. El catálogo del Core (NRF)** | La administración mira la lista interna del edificio: "¿quién cuida la seguridad? ¿quién entrega las llaves?". |
| **6. Autenticación** | La seguridad revisa el documento — ¿eres tú de verdad? Si no coincide, no entra. |
| **7. Solicitud de sesión de datos** | Aprobado, pides una "línea" para enviar y recibir cosas. |
| **8. Programa el plano de usuario** | La administración avisa al pasillo de entregas: "prepara el camino de las cartas de esta persona". |
| **9. El UE recibe IP** | Recibes la **llave de la habitación** y una **dirección** — ahora puedes recibir correspondencia. |
| **10. Datos — ida** | Envías una carta hacia afuera. |
| **11. Salida — internet / llamada** | La carta sale del edificio hacia el mundo (la internet). |
| **12. Datos — vuelta** | La respuesta llega y sube de vuelta hasta ti. |
| **13. Recolección de datos (RIC)** | Un **supervisor astuto** empieza a anotar cómo está el movimiento (velocidad, ocupación) — los números vienen de la antena. |
| **14. Acción en la antena (RIC)** | El supervisor decide y **ajusta el flujo en tiempo real** (abre más espacio, cambia la fila). Es él "moviendo la antena" a distancia. |
| **15. Planificador de largo plazo** | Un planificador estudia el histórico y envía **reglas** al supervisor. Es aquí donde entra la **inteligencia artificial**. |
| **16. El camino completo** | El edificio entero de una vez: lo que es obligatorio y lo que es el extra "inteligente". |

---

## Dos colores, dos tipos de paso

- 🟢 **obligatorio** — tiene que ocurrir, si no, no entras o no navegas. Es la
  **línea de la vida** (pantallas 2 a 12).
- 🔵 **opcional** — el extra "inteligente" (el supervisor y el planificador, pantallas 13 a
  15). La red funciona sin él — pero es aquí donde vive la IA.

## La idea más importante: "quién decide" ≠ "quién carga"

En el edificio, **la administración** (que decide, autoriza, organiza) está **separada** de
los **pasillos** (por donde las cartas realmente andan). Esto tiene un nombre feo (CUPS),
pero la idea es simple y poderosa: se puede **cambiar un pasillo sin parar la
administración**. Es lo que permite el próximo truco 👇

---

## Proyecto 1 (Open5GS) — casi igual, con 2 diferencias

La historia es la misma (el celular llegando al edificio). Cambia solo esto:

1. **No tiene el supervisor astuto** (el RIC). El P1 va de la pantalla 1 hasta "el camino
   completo", sin las partes de inteligencia.
2. **Tiene un final extra: el pasillo de reserva** (el *failover*). Si el pasillo de
   entregas se cae, la administración **cambia a un pasillo de reserva al instante** — y
   tú sigues navegando sin darte cuenta. Es la prueba de que separar "quién decide"
   de "quién carga" vale la pena.

---

## Cómo usarlo para que caiga la ficha

1. Abre el **Viaje del UE** en el panel y esta guía al lado.
2. Haz clic en **Siguiente** despacio, leyendo la leyenda de la pantalla **y** la línea de aquí.
3. Pasa **2 o 3 veces**. En la segunda, ya vas a anticipar lo que viene.
4. Solo después, si quieres, mira los nombres técnicos — ahora tienen un lugar en la
   historia, ya no son siglas sueltas.

> Consejo: el mismo diagrama tiene un modo **"Flujo de datos"** (bolitas caminando) y un
> **"Tour"** por capas. El **Viaje** es la versión paso a paso, guiada — empieza
> por ella.
