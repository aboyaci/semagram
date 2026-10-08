# Dictionary

Generated from `dictionary/core.json` and packs: attention. Do not edit by hand.

## Grammar: particles and linkers

| Glyph | English | Türkçe | Transparency | Notes |
|---|---|---|---|---|
| 🔷 | [sentence end] | [cümle sonu] | opaque | The only delimiter. One sentence per line is house style; a line wrap can never break a sentence. |
| 💬 | [says] | [der] | transparent | Closes a speaker label: 🐟💬 = the fish says. Scopes to the end of the sentence. Also the root WORDS, always first in a compound; as a label closer it is always last, so the two never collide. |
| 🏷️ | [name follows] | [özel ad] | translucent | A cartouche; the text after it is a proper name in any script, read as one word. Prefix a category glyph so a reader who cannot read the script still knows what kind of thing it is: 👤🏷️Mehmet person, 📍🏷️İstanbul place, 👥🏷️Anthropic group, 📦🏷️Transformer thing, 🐾🏷️Karabaş animal. A name used more than twice is bound once at the top of the document: 👦 ≔ 👤🏷️Mehmet. Never translate a name. |
| ≔ | [define] | [tanımla] | translucent | Declares a Layer 2 word: 🤖 ≔ 🏷️Transformer. Math script. |
| 📜 | [the idea of] | [-lik, -lık] | translucent | Determinative, Egyptian style: 🧠📈📜 = learning (the abstraction). Chips at the abstract-vocabulary wall. |
| 🟡 | we think | sanıyoruz | translucent | Confidence opener. Unmarked = asserted. Shorthand for 🙋💭💬. |
| 🔴 | we guess | tahminimiz | translucent | Confidence opener. Speculation. |
| ➡️ | so / therefore | bu yüzden | translucent | Opens a sentence; inherits the confidence of the previous one. |
| ⬅️ | because | çünkü | translucent |  |
| 🔀 | but | ama | translucent |  |
| ∧ | and | ve | opaque | Math script. ➕ rejected: collides with arithmetic plus. OPEN: no emoji candidate yet. |
| ∨ | or (inclusive) | veya | opaque | Math script. Defined inclusive, which English never settled. |
| 🔺 | if | eğer | opaque | Opens the condition sentence; the consequence follows as the next sentence. |

## Grammar: modifiers (attach to the left)

| Glyph | English | Türkçe | Transparency | Notes |
|---|---|---|---|---|
| ❌ | not / no / false | değil / yok / yanlış | transparent | Postfix. Ends a word and negates the whole word. Standing alone in the patient slot = 'the false'. Never use ❎ (renders green on some platforms). |
| 🌑 | none / no (quantity) | hiç | translucent | Moon scale = proportions. 🌑 after a noun = zero of them. NSM: NOT (quantity). |
| 🌘 | a small part of | küçük bir kısmı | translucent |  |
| 🌗 | half | yarısı | transparent |  |
| 🌔 | most | çoğu | translucent |  NSM: MUCH/MANY (proportional). |
| 🌕 | all | hepsi | translucent | 'Some' = 🌑❌ (not none), the actual existential quantifier. NSM: ALL. |
| 👍 | good | iyi | transparent | 👍📈 = better. ❤️👍 = happy. NSM: GOOD. |
| 👎 | bad | kötü | transparent |  NSM: BAD. |
| 🐘 | big | büyük | translucent | Means BIG, never elephant. 🕐🐘 long time, 📏🐘 far, 🧮🐘 many. NSM: BIG. |
| 🐜 | small | küçük | translucent | Means SMALL, never ant. NSM: SMALL. |
| 📈 | more / increase | daha / artış | transparent | 🧠📈 learn. Standing first in a sentence it is the predicate 'grows'. NSM: MORE. |
| 📉 | less / decrease | daha az / azalış | transparent | 🧠📉 forget. |
| ‼️ | very | çok | translucent |  NSM: VERY. |
| ⬆️ | above / up | üst / yukarı | transparent | Sentence-initial: predicate 'is above'. NSM: ABOVE. |
| ⬇️ | below / down | alt / aşağı | transparent |  NSM: BELOW. |

## Layer 0: semantic primes

| Glyph | English | Türkçe | Transparency | Notes |
|---|---|---|---|---|
| ✅ | true / yes | doğru / evet | transparent |  NSM: TRUE. |
| 🎲 | maybe | belki | translucent |  NSM: MAYBE. |
| 💪 | can | -ebilmek | translucent | 💪❌ = cannot. NSM: CAN. |
| 🙋 | I | ben | translucent | 🙋🙋 = we (reduplication = plural). As a trailing modifier = my: 🏠🙋 = my home. NSM: I. |
| 🫵 | you | sen | transparent |  NSM: YOU. |
| 👤 | someone | biri | transparent |  NSM: SOMEONE. |
| 📦 | something / thing | bir şey | translucent |  NSM: SOMETHING. |
| 👥 | people | insanlar | transparent |  NSM: PEOPLE. |
| 🧍 | body | beden | transparent |  NSM: BODY. |
| 👉 | this / it / he / she (back-reference) | bu / o | transparent | One pronoun for he, she, it, this, that, as Turkish o. Points at a thing or at the whole previous sentence. When two referents compete, prefix a category glyph: 👤👉 the person, 📦👉 the thing, 🐾👉 the animal. Anything that recurs should be bound to a glyph with ≔ instead. Never gendered. NSM: THIS. |
| 👈 | other | öteki / diğer | translucent | Not derivable from 🟰❌ (different): the other mouse can be identical. 👈🌕 = all others; X∧👈🌑 = only X. NSM: OTHER. |
| 🟰 | same | aynı | transparent | 🟰❌ = different. NSM: SAME. |
| 🗂️ | kind / type | tür | translucent |  NSM: KIND. |
| 🧩 | part (of) | parça | transparent | Two-place: 🧩 X Y = X is part of Y. Used backwards for 'have'. NSM: PART. |
| 💭 | think | düşünmek | transparent | Bubble = the process; 🧠 = what is stored. NSM: THINK. |
| 🧠 | know | bilmek | translucent |  NSM: KNOW. |
| 🎯 | want | istemek | translucent |  NSM: WANT. |
| ❤️ | feel | hissetmek | translucent | Reads as 'love' cold: a near miss, tolerated. ❤️👍 happy, ❤️👎 sad. NSM: FEEL. |
| 👁️ | see / eye | görmek / göz | transparent |  NSM: SEE. |
| 👂 | hear / ear | duymak / kulak | transparent |  NSM: HEAR. |
| 🗣️ | say | söylemek | transparent | In dialogue use the 💬 label instead. 🗣️❌ = does not say. NSM: SAY. |
| 🤜 | do | yapmak | translucent | Hand = agency. 🤜🟰 = repeat (do same). 🤜👈 = other doings (stand-in for 'task'). NSM: DO. |
| 💥 | happen | olmak | translucent |  NSM: HAPPEN. |
| 🏃 | move | hareket etmek | transparent | 🏃⬆️ go up / jump, 🏃⬇️ go down / dive. NSM: MOVE. |
| ∃ | there is / exists | var | opaque | Math script. No picture of existence is possible. NSM: THERE IS. |
| 🌱 | live | yaşamak | translucent |  NSM: LIVE. |
| 💀 | die | ölmek | transparent | Flagged: slang reads it as 'dying laughing'. Literal reading holds in formal text. NSM: DIE. |
| 🕐 | time | zaman | transparent | 🕐👉 now (also resets tense). 🕐🐘 long time, 🕐🐜 short time. NSM: TIME. |
| ⏪ | before / past | önce / geçmiş | translucent | Tense is sticky: ⏪🔷 alone sets the frame for everything after, until 🕐👉🔷 or ⏩🔷. NSM: BEFORE. |
| ⏩ | after / future | sonra / gelecek | translucent |  NSM: AFTER. |
| 📍 | place | yer | transparent | 📍👉 here, 📍⬆️ the place above. NSM: WHERE/PLACE. |
| 📥 | inside / in | içinde | translucent | Two-place: 📥 X Y = X is in Y. NSM: INSIDE. |
| 📤 | outside | dışında | translucent |  |
| ↔️ | side / beside | yan | translucent |  NSM: SIDE. |
| 🪞 | like / similar to | gibi | translucent |  NSM: LIKE. |

## Layer 1: core roots

| Glyph | English | Türkçe | Transparency | Notes |
|---|---|---|---|---|
| 📏 | distance / length | uzaklık / uzunluk | transparent | 📏🐘 far, 📏🐜 near, 📏🌑 touching (zero distance). |
| 🧮 | number / count | sayı | translucent | 🧮🐘 many (absolute), 🧮🐜 few. Moons are proportions, 🧮 is counts. |
| ☀️ | sun / day | güneş / gün | transparent |  |
| 🌃 | night | gece | transparent |  |
| 💧 | water | su | transparent |  |
| 🔥 | fire / hot | ateş / sıcak | transparent |  |
| ❄️ | ice / cold | buz / soğuk | transparent |  |
| 🪨 | stone | taş | transparent |  |
| 🌍 | world | dünya | transparent |  |
| 🌬️ | air / wind | hava / rüzgâr | translucent |  |
| ⛰️ | mountain | dağ | transparent |  |
| 🌊 | sea | deniz | transparent |  |
| 🌳 | tree | ağaç | transparent |  |
| 🌿 | plant | bitki | transparent | Promoted: honest compound 📦🌱🏃❌ ran to 3+ glyphs. |
| 🐾 | animal | hayvan | transparent |  |
| 🐟 | fish | balık | transparent |  |
| 🐦 | bird | kuş | transparent |  |
| 🐭 | mouse | fare | transparent |  |
| 🥚 | egg | yumurta | transparent |  |
| 🦴 | bone | kemik | transparent |  |
| 🩸 | blood | kan | transparent |  |
| 🦠 | disease / germ | hastalık / mikrop | translucent |  |
| 👶 | child | çocuk | transparent | Only face allowed: meaning is not in the expression. |
| ✋ | hand | el | transparent |  |
| 🦶 | foot | ayak | transparent |  |
| 👄 | mouth | ağız | transparent |  |
| 🦷 | tooth | diş | transparent |  |
| 👃 | nose / smell | burun / koklamak | transparent |  |
| 🍽️ | eat | yemek | transparent |  |
| 💤 | sleep | uyumak | transparent |  |
| 🎁 | give | vermek | translucent |  |
| 🔨 | make / build | yapmak / inşa etmek | transparent |  |
| 🔧 | use / tool | kullanmak / araç | translucent |  |
| ✂️ | cut | kesmek | transparent |  |
| 🔗 | join / relation | bağlamak / bağ | translucent |  |
| 🔍 | search | aramak | transparent |  |
| 📖 | read | okumak | transparent |  |
| ✍️ | write | yazmak | transparent |  |
| 🔓 | open | açmak | transparent |  |
| 🔒 | close | kapatmak | transparent |  |
| 🐣 | new / begin | yeni / başlamak | translucent | Hatchling. 🗺️🐣 = a new model. |
| 🏁 | end / finish | bitmek / son | translucent |  |
| 🦋 | change | değişmek | translucent |  |
| 🤝 | agree | anlaşmak | transparent | Rule 6: give a glyph the meaning people already read into it. |
| ⚔️ | oppose / fight | karşı çıkmak | transparent |  |
| ⚖️ | compare | karşılaştırmak | translucent | ⚖️🧮 = measure. |
| 🏠 | house / home | ev | transparent |  |
| 🛣️ | path / method | yol / yöntem | translucent |  |
| 🍞 | food | yiyecek | translucent |  |
| 💰 | money / cost | para / maliyet | transparent |  |
| ⚙️ | machine | makine | translucent |  |
| 💻 | computer | bilgisayar | transparent |  |
| ⚡ | energy / electricity | enerji / elektrik | transparent |  |
| 🔦 | light | ışık | translucent | 💡 was taken by 'idea' (rule 6). |
| 🔊 | sound | ses | transparent |  |
| 🎨 | color | renk | translucent |  |
| 💡 | idea | fikir | transparent |  |
| 🗺️ | model / map | model / harita | translucent |  |
| 🧪 | experiment / test | deney | transparent |  |
| 📊 | data | veri | transparent |  |
| 🧺 | group / set | küme / grup | translucent |  |
| 🪜 | order / level | sıra / düzey | translucent |  |
| 🐇 | fast | hızlı | translucent |  |
| 🐢 | slow | yavaş | translucent |  |
| 🏆 | best | en iyi | transparent | Promoted from the abstract: 'better than all others' was a whole clause. |
| ∥ | parallel | paralel | translucent | Math script. |

## Layer 2: domain packs

| Glyph | English | Türkçe | Transparency | Notes |
|---|---|---|---|---|
| 🤖 | Transformer | Transformer | translucent | 🤖 ≔ 🏷️Transformer |
| 👀 | attention | dikkat (mekanizması) | transparent |  |
| 🔁 | recurrence / RNN | yineleme / RNN | translucent |  |
| 🪟 | convolution | evrişim | translucent | A sliding window. |

## Declared compounds

Head first. Under the no-break rule a compound must be declared before it can be read.

| Glyphs | English | Türkçe | Source |
|---|---|---|---|
| 🙋🙋 | we | biz | core |
| 🕐👉 | now (resets tense) | şimdi | core |
| 📍👉 | here | burası | core |
| 🟰❌ | different | farklı | core |
| 🌑❌ | some (not none) | bazı | core |
| 🧠📈 | learn | öğrenmek | core |
| 🧠📉 | forget | unutmak | core |
| 💪🧠📈 | learnability | öğrenilebilirlik | core |
| 💭✅ | believe | inanmak | core |
| ❤️👍 | happy | mutlu | core |
| ❤️👎 | sad | üzgün | core |
| 👍📈 | better | daha iyi | core |
| 🤜🟰 | repeat | tekrarlamak | core |
| ⚖️🧮 | measure | ölçmek | core |
| 🧩🌕 | whole | bütün | core |
| 🕐🐘 | long time | uzun süre | core |
| 🕐🐜 | short time | kısa süre | core |
| 📏🐘 | far | uzak | core |
| 📏🐜 | near | yakın | core |
| 📏🌑 | touching | temas | core |
| 🧮🐘 | many | çok (sayıca) | core |
| 🧮🐜 | few | az (sayıca) | core |
| 🏃⬆️ | go up / jump | yukarı çıkmak / zıplamak | core |
| 🏃⬇️ | go down / dive | aşağı inmek / dalmak | core |
| 👈🌕 | all others | diğerlerinin hepsi | core |
| 🤜👈 | other doings / tasks | başka işler | core |
| 💬🦋 | translation (words change) | çeviri | core |
| 📖⚙️ | encoder (reading machine) | kodlayıcı | core |
| ✍️⚙️ | decoder (writing machine) | kod çözücü | core |
| 🧺🗺️ | ensemble (group of models) | topluluk modeli | core |
| ✂️🌳 | parsing (cutting trees) | ayrıştırma | core |
| 🧠📈📜 | learning (the idea of) | öğrenme | core |
| 🗺️🐣 | new model | yeni model | core |
| 🏷️BLEU | BLEU score | BLEU puanı | attention |
| 🏷️GPU | GPU | GPU | attention |
| 🏷️EN | English | İngilizce | attention |
| 🏷️DE | German | Almanca | attention |
| 🏷️FR | French | Fransızca | attention |
