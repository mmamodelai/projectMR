BEGIN;

-- Update products for: The Original Z
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$The Original Z(popularly known under an infringing candy name) is anindicahybrid marijuana strain bred from an alleged mix ofGrape ApeandGrapefruitthat is crossed with another undisclosed strain. This sweet, tropical confection-flavored cultivar came to market in the 2010s. According to the story, the cultivar came from an individual dubbed Gas Station Bob. Working as Terp Hogz, the growers Fields and Tony Mendo popularized Z with the help of 3rd Gen Family's Brandon Parker—growing the strain, entering it into contests, and making new crosses. The Original Z won 1st Place at the 2016 Emerald Cup, the 2023 King of Z Hill, and has placed in several Cannabis Cups in San Francisco and Michigan. Both Terp Hogz and 3rd Gen Fam—as well as other breeders—continue to refine the varietal.  In 2023, Terp Hogz announced they will use the name "The Original Z," as part of a settlement with a candy company over alleged trademark infringement.  This strain features medium-sized, spongy greencolasthat with asweet,tropicalblend offruitflavors. The effects of The Original Z are calming, leaving consumersfocused, alert, andhappywhilerelaxingthe body to help unwind any time of day.$$,
    leafly_rating = 4.492610837438423,
    leafly_review_count = 1015,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Alert"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/6VF5EvUTjqZPKFVOQAAY_Zkittlez.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/zkittlez',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%zkittlez%' OR name ILIKE '%skittlez%');



-- Update products for: White Widow
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$White Widowis ahybridweed strain made from a genetic cross between a Braziliansativalandrace and a resin-heavy South Indianindica. This strain is 60% sativa and 40% indica. White Widow is one of the most famous strains worldwide, first bred in the Netherlands by Green House Seeds in the 1990s. Its buds are white with crystal resin, warning you of the potent effects to come. A powerful burst of euphoria and energy breaks through immediately, stimulating both conversation and creativity. White Widow is 15% THC, making this strain an ideal choice for moderate cannabis consumers. Leafly customers tell us White Widow effects include feelingenergetic,talkative, andcreative. Medical marijuana patients often choose White Widow when dealing with symptoms associated withstress,anxiety, andpain. White Widow features flavors likewoody,spicy/herbal, andearthy. The dominant terpenes of this strain aremyrceneandcaryophyllene, though growing conditions and strain phenotypes may impact the exact blend. The average price of White Widow typically ranges from $8-$12 per gram. White Widow is a balanced hybrid that can be enjoyed by both indica and sativa lovers. It has a flowering time of 8-9 weeks and can be grown indoors or outdoors in mild climates. It produces chunky and conical buds with a loose and fluffy texture that are easy to break up despite their stickiness. If you’ve smoked, dabbed, or consumed White Widow, tell us about your experience by leaving a strain review.$$,
    leafly_rating = 4.290030211480363,
    leafly_review_count = 4634,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"a Brazilian sativa landrace","a resin-heavy South Indian indica"}'::TEXT[],
    lineage = $$a Brazilian sativa landrace x a resin-heavy South Indian indica$$,
    image_url = 'https://images.leafly.com/flower-images/white-widow.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/white-widow',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%white%widow%');



-- Update products for: Trainwreck
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Trainwreckis a mind-bending, potentsativawith effects that hit like a freight train.MexicanandThaisativas were bred withAfghaniindicasto produce this Northern California staple, passing on asweetlemonandspicypinearoma. Trainwreck begins its speedy hurtle through the mind with a surge ofeuphoria, awakeningcreativityandhappiness.Migraines,pain, andarthritisare mowed down by Trainwreck’s high-THC content, and many patients also use it for relief ofanxiety,ADD/ADHD, andPTSD.  There are many stories about the origin of the name. Some say growers grew it among a train wreck in Arcata, CA. Others say the plant's sprawling growth resembled a train wreck.$$,
    leafly_rating = 4.211706102117061,
    leafly_review_count = 3212,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/trainwreck.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/trainwreck',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%trainwreck%');



-- Update products for: Skywalker OG
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Skywalker OGis an Indica-dominanthybridcannabis strain with a potent THC content ranging from 20% to 30%. It is a cross betweenMazarandBlueberry OGstrains. The dominant terpenes found in Skywalker OG aremyrcene,caryophyllene, andlimonene. Skywalker OG is well-known for itsrelaxingandeuphoriceffects, making it an excellent choice forstressrelief andpainmanagement. This strain is often used to alleviate symptoms ofanxiety,depression, andinsomnia. The strain's name pays homage to the Star Wars franchise, featuring the namesake of Luke Skywalker himself. Skywalker OG's creators chose to name the strain after the Jedi hero due to its potent, "forceful" effects. When it comes to taste and aroma, Skywalker OG has aspicy,herbalflavor with hints ofearthyundertones. The top flavors and aromas includediesel,pine, andspicy herbalnotes.$$,
    leafly_rating = 4.464022662889518,
    leafly_review_count = 1765,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Mazar","Blueberry OG strains"}'::TEXT[],
    lineage = $$Mazar x Blueberry OG strains$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/long-fluffy-wispy/strain-2.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/skywalker-og',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%skywalker%og%' OR (name ILIKE '%skywalker%' AND name ILIKE '%og%'));



-- Update products for: Headband
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Headband, also known as simply "HB," is a hybrid marijuana strain and love-child of cannabis’ power couple,OG KushandSour Diesel. The smooth, creamy smoke is accented by flavors oflemonsanddieselwhile the long-lasting effects are great forpainrelief, helping you torelax, and to combat elevatedstresslevels. Many report that the effects create a slight pressure around the crown of their head and feels as though they are wearing a headband. The effects have been known to come on slow, so pace yourself with this potenthybrid.$$,
    leafly_rating = 4.213008748573603,
    leafly_review_count = 2629,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/3EbkAKSsTfyyIsmMfygd_Headband_jman_hdr.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/headband',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%headband%');




COMMIT;