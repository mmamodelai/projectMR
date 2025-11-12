BEGIN;

-- Update products for: Purple Haze
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Purple Hazeis asativamarijuana strain popularized by Jimi Hendrix’s 1967 classic song, Purple Haze. This strain delivers a dreamy burst ofeuphoriathat brings veteran consumers back to their psychedelic heyday. This nostalgic sativa staple remains cherished for itshigh energycerebral stimulation that awakenscreativityand blissfulcontentmentthroughout the day. Purple Haze is believed to have descended from parent strainsPurple ThaiandHaze, which pass on a mix ofsweetandearthyflavors underscored by notes ofberryand sharpspice. Purple Haze buds typically acquire vibrant hues of lavender that further justify the naming of this strain.$$,
    leafly_rating = 4.2223113964687,
    leafly_review_count = 1246,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"strains Purple Thai","Haze"}'::TEXT[],
    lineage = $$strains Purple Thai x Haze$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/purple/strain-10.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/purple-haze',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%purple%haze%');



-- Update products for: Chemdawg
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Chemdawg, officially named "Chemdog," is a hybrid marijuana strain grown and spread by the breeder Chemdog since 1991. In a Leafly interview, Chemdog relates how Chemdog came from what was thought to be Northern California bag seed, via a Colorado Grateful Dead concert. Chem 91, Chem 4, and Chem Sis are all variations on Chemdog. The original name Chemdog came from two names for the same bud "Chem" and "Dog bud." Chemdog evolved into the variation 'Chemdawg' over time and distance as other growers and breeders propagated it, with the latter name becoming more dominant. Leafly customers tell us Chemdawg effects includefeelingeuphoric,uplifted, andcreative. Medical marijuana patients often choose Chemdawg when dealing with symptoms associated withstress,anxiety, andpain. Chemdog is a staple strain in cannabis and may be a source of powerhouse strains likeSour DieselandOG Kush, Chemdog is known for its distinct,diesel-like aroma.Pungentand sharp, you’ll be able to smell this strain from a mile away. Cannabis newbies be warned: Chemdog tends to be very potent. Consumers can expect to have a cerebral experience, coupled with a strong heavy-bodied feeling.$$,
    leafly_rating = 4.263916700040048,
    leafly_review_count = 2497,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Sour","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/generic/strain-1.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/chemdawg',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%chemdawg%' OR name ILIKE '%chemdog%');



-- Update products for: Mango Kush
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$TheMango Kushmarijuana strain tastes similar to the actualmangofruit, with a distinct kush flavor and hints ofpineon the exhale. Its buds are covered with orangepistilsand are described as very dense. The plant has an average growth height of 4-5 feet. Flowering is 9-11 weeks and is a favorite with both indoor and outdoor growers. The buds have thick shiny trichomes which are evident when the bud is broken apart. The smell and taste are the same and described as mango and banana.$$,
    leafly_rating = 4.238242097147263,
    leafly_review_count = 1297,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/mango-kush.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/mango-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%mango%kush%');



-- Update products for: Clementine
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Clementineis a energizing sativa-dominant strain that is made by crossingTangiewithLemon Skunk. This strain is loved for its sweet taste and citrus aroma. Leafly users say Clementine is perfect for a wake and bake or activating your third eye to increase your focus. Clementine has won awards including the best sativa concentrate in 2015.$$,
    leafly_rating = 4.415929203539823,
    leafly_review_count = 565,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Strawberry","Nutty","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Tangie","Lemon Skunk"}'::TEXT[],
    lineage = $$Tangie x Lemon Skunk$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/QNQ0kFSQ9Cf1v5ffgbWl_Clementine.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/clementine',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%clementine%');



-- Update products for: Bubba Kush
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Bubba Kush, also known as "BK," "Bubba," and "Bubba OG Kush" is anindicamarijuana strain from Florida that has gained notoriety in the US and beyond for its heavy tranquilizing effects. Sweet hashish flavors with subtle notes of chocolate and coffee come through on the exhale, delighting the palate as powerful relaxation takes over. From head to toe, muscles ease with heaviness as dreamy euphoria blankets the mind, crushing stress while bringing happy moods. Bubba Kush exhibits a distinctive, bulky bud structure with hues that range from forest green to pale purple.$$,
    leafly_rating = 4.258739333883843,
    leafly_review_count = 3633,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{}'::TEXT[],
    lineage = $$$$,
    image_url = 'https://images.leafly.com/flower-images/bubba-kush.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/bubba-kush',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%bubba%kush%');




COMMIT;