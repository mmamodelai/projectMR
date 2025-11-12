BEGIN;

-- Update products for: Fire OG
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Fire OG, also known as "Fire OG Kush," is a indica-dominanthybridmarijuana strain made by crossingOG KushandSFV OG Kush. This strain has an aroma similar to Lemon Pledge and has euphoric effects that are potent and long-lasting. Fire OG is one of the strongest OG strains, and is a fan favorite among consumers who have a high THC tolerance. Fire OG gets its name from the frosty red hairs that make the strain appear to look like it is on fire. Fire OG plants typically flower in 9-10 weeks.$$,
    leafly_rating = 4.374800637958533,
    leafly_review_count = 1254,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"OG Kush","SFV OG Kush"}'::TEXT[],
    lineage = $$OG Kush x SFV OG Kush$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/UILdlZQQuN969injI7OQ_FireOG.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/fire-og',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%fire%og%');



-- Update products for: GG4
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Original Glue is ahybridweed strain made from a genetic cross between Chem’s Sister,Sour Dubb, andChocolate Diesel. This strain is 37%sativaand 63%indica. Also known as “GG4”, Original Glue is a potent strain that delivers heavy-handed euphoria and relaxation, leaving you feeling “glued” to the couch. Its chunky, resin-covered buds fill the room with pungent earthy and sour aromas inherited from its parent strains. Original Glue is 20% THC, making this strain an ideal choice for experienced cannabis consumers. Leafly customers tell us Original Glue effects include feelingrelaxed,sleepy, andhungry. Medical marijuana patients often choose Original Glue when dealing with symptoms associated withstress,anxiety, andpain. Bred by GG Strains LLC, Original Glue features flavors likepungent,pine, andearthy. The dominant terpene of this strain iscaryophyllene. The average price of Original Glue typically ranges from $10-$15 per gram. Original Glue is a multiple award-winning strain that has taken first place in both the Michigan and Los Angeles 2014 Cannabis Cups, as well as the High Times Jamaican World Cup in 2015. It is a fast-growing strain that produces large yields of sticky buds with a flowering time of 9-10 weeks. If you’ve smoked, dabbed, or consumed Original Glue, tell us about your experience by leaving a strain review.$$,
    leafly_rating = 4.639040348964013,
    leafly_review_count = 5502,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/gg-4.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/original-glue',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%gorilla%glue%' OR name ILIKE '%gg4%' OR name ILIKE '%gg #4%');



-- Update products for: Sherbert
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Sherbert, also known as "Sherbet", "Sherbert OG", "Sunset Sherbet", and "Sunset Sherbert" is an indica-dominant hybrid marijuana strain made by crossingGirl Scout CookieswithPink Panties. This strain exhibits powerful, full-body effects that are elevated by a jolt of cerebral energy and carefree state of mind. Sherbet boasts a THC level of 18% and may be overwhelming to novice cannabis consumers. The high potency of Sherbert makes it an ideal choice for medical marijuana patients seeking relief from symptoms associated withstress,tension, and mood disorders. This strain features a sweet, dessert-like flavor profile with notes of skunky citrus, sweet berry, and candy. The average price per gram of Sherbert is $20, but may vary based on your location. According to growers, Sherbert flowers into oblong fluffy nugs with rich trichome coverage and dark amber hairs throughout light and dark green foliage. This strain was originally bred by Mr. Sherbinski, who bred Sherbert intentionally to inherit the genetic lineage of its parent strain Girl Scout Cookies.$$,
    leafly_rating = 4.548787699586044,
    leafly_review_count = 1691,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Girl Scout Cookies","Pink Panties"}'::TEXT[],
    lineage = $$Girl Scout Cookies x Pink Panties$$,
    image_url = 'https://images.leafly.com/flower-images/sunset-sherbert.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/sunset-sherbert',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%sunset%sherbet%' OR name ILIKE '%sherbert%');


COMMIT;


COMMIT;