# Creative Hypothesis Matrix

## Core Product

Paid natal report / full natal breakdown for the Ukrainian astrology audience.

## Funnel Sources

- `quiz_short` — current best performer / benchmark.
- `quiz_journey` — pseudo-chat discovery route.
- `quiz_journey_land` — landing/sales explanation route.
- `quiz_journey_steps` — guided step-by-step route.

## Pain Buckets

1. Repeating scenario
   - Feeling: "I keep ending up in the same situation."
   - Hooks:
     - "Ты снова попадаешь в один и тот же сценарий?"
     - "Если в жизни все повторяется, это не всегда случайность."
     - "Твой главный сценарий может быть виден в натальной карте."
   - Best funnels: `quiz_journey`, `quiz_journey_steps`.

2. Relationships loop
   - Feeling: "I choose wrong people / I give more than I receive."
   - Hooks:
     - "Почему в отношениях ты снова берешь всё на себя?"
     - "Если тебя часто не слышат, посмотри не на знак, а на карту."
     - "Повторяющийся сценарий в отношениях может быть не случайным."
   - Best funnels: `quiz_short`, `quiz_journey`.

3. Money and energy leak
   - Feeling: "Money comes but does not stay / energy drains."
   - Hooks:
     - "Деньги приходят, но не держатся?"
     - "Иногда проблема не в дисциплине, а в повторяющемся паттерне."
     - "Где ты теряешь деньги и энергию — карта может подсветить."
   - Best funnels: `quiz_journey_land`, `quiz_journey_steps`.

4. Anti-horoscope / personal map
   - Feeling: "Generic horoscopes are too vague."
   - Hooks:
     - "Гороскоп говорит всем одно. Натальная карта показывает твой механизм."
     - "Это не прогноз для всех Рыб/Львов/Овнов. Это твоя карта."
     - "Не знак зодиака. Полная картина по дате рождения."
   - Best funnels: `quiz_short`, `quiz_journey_land`.

5. Hidden potential / stuck identity
   - Feeling: "I know I can do more, but something holds me back."
   - Hooks:
     - "Ты чувствуешь, что можешь больше, но будто что-то держит изнутри?"
     - "В карте видно не только характер, но и где ты себя тормозишь."
     - "Иногда твоя сильная сторона выглядит как проблема, пока ты ее не понимаешь."
   - Best funnels: `quiz_journey`, `quiz_short`.

6. Emotional core / overthinking
   - Feeling: "I keep replaying situations in my head."
   - Hooks:
     - "Почему ты прокручиваешь одно и то же в голове?"
     - "Эмоции тянут вниз не просто так. В карте часто есть подсказка."
     - "Твоя реакция может быть паттерном, а не слабостью."
   - Best funnels: `quiz_journey`, `quiz_journey_steps`.

## Creative Formats

- POV confession: "Я думала, что просто выбираю не тех людей..."
- Direct hook over mystical background.
- Site UI reveal: birth date -> chart -> insight -> CTA.
- Myth busting: horoscope vs natal report.
- Mini-story: repeated loop -> insight -> quiz CTA.
- Static premium background + voiceover.
- Screen recording with subtitles and cursor/tap emphasis.

## Daily UBT Batch Template

For each daily batch, produce 5-10 organic tests:

- 2 benchmark/control creatives to `quiz_short`.
- 2 creatives to `quiz_journey`.
- 2 creatives to `quiz_journey_land`.
- 2 creatives to `quiz_journey_steps`.
- 1-2 wildcards based on recent winners.

## Promotion Rule

Only promote to paid ads after organic signal, for example:

- unusually high 3-second hold,
- strong completion rate,
- comments/saves above batch average,
- clear click/purchase signal,
- or repeated organic reach across variants of the same angle.

## Future Tooling

When ready, add APIs:

- OpenAI image generation / DALL-E for controlled static backgrounds.
- ElevenLabs for voiceover generation.
- Later: Veo or another video generation tool for custom B-roll.

The API tools should generate into the same intake folders, then `scripts/intake_assets.py` imports them.
