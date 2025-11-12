BEGIN;

-- Update products for: Lemon Haze
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Lemon Hazeis asativamarijuana strain that smells and tastes like fresh peeled lemon slices. Lemon Haze is made by crossingLemon SkunkwithSilver Haze. Its buds appear to be green and yellow with amber hairs on the trichomes, giving it the yellow tint.$$,
    leafly_rating = 4.205893464299207,
    leafly_review_count = 2647,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Lemon Skunk","Silver Haze"}'::TEXT[],
    lineage = $$Lemon Skunk x Silver Haze$$,
    image_url = 'https://images.leafly.com/flower-images/defaults/red-orange-amber/strain-4.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/lemon-haze',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%lemon%haze%');



-- Update products for: Pineapple Express
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Pineapple Expressis a sativa-dominanthybrid marijuana strainmade by crossingTrainwreckwithHawaiian. While this strain rose to fame on the silver screen in 2008 amidst the release ofPineapple Express,it is a real strain that you can find on the shelves of dispensaries across the country.Since then, this strain has become a favorite in the hearts and minds of cannabis lovers. Pineapple Express produces long-lastingenergetic effectsthat you can feel right away. Pineapple Express is 20% THC and may make you feelbuzzy,alert, andcreative. The best time to smoke Pineapple Express is in the morning, afternoon, or early evening hours. In terms of flavor, this strain packs a punch to your pallet withbright citrusnotes infused withpineappleandearthypine, thanks to the terpenes ofcaryophyllenelimoneneandOcimene. Medical marijuana patients choose Pineapple Express to relieve symptoms associated withdepression,pain, andfatigue. The average price per gram of Pineapple Express is $20.$$,
    leafly_rating = 4.404226618705036,
    leafly_review_count = 4448,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Alert"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Fruity","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Trainwreck","Hawaiian"}'::TEXT[],
    lineage = $$Trainwreck x Hawaiian$$,
    image_url = 'https://images.leafly.com/flower-images/pineapple-express.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/pineapple-express',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%pineapple%express%');



-- Update products for: Wedding Cake
UPDATE products
SET
    leafly_strain_type = 'Indica',
    leafly_description = $$Wedding Cake, also known as "Triangle Mints #23," is a potent type ofindica-hybrid marijuana strainmade by crossingTriangle KushwithAnimal Mints. Fun fact: In Canada, this strain is known asPink Cookies. The Wedding Cake strain providesrelaxingandeuphoric effectsthat calm the body and mind. This strain yields a rich and tangy flavor profile with undertones ofearthy pepper. Medical marijuana patients choose Wedding Cake to help relieve symptoms associated withpain,insomniaandappetite loss. Consumers with a low THC tolerance should enjoy this strain with an extra slice of care due to its high THC content. Wedding Cake has soared in popularity over the years and was namedLeafly Strain of the Yearin 2019.$$,
    leafly_rating = 4.553571428571429,
    leafly_review_count = 2632,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Triangle Kush","Animal Mints"}'::TEXT[],
    lineage = $$Triangle Kush x Animal Mints$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/m2y50HYRBu0dHY4JSdSx_wedding-cake_jman.jpg?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/wedding-cake',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%wedding%cake%');



-- Update products for: Strawberry Cough
UPDATE products
SET
    leafly_strain_type = 'Sativa',
    leafly_description = $$Known for its sweet smell of fresh strawberries and an expanding sensation that can make even the most seasoned consumer cough,Strawberry Coughis a potentsativamarijuana strain with mysterious genetic origins. However, Strawberry Cough is thought to be a cross ofHazeandStrawberry Fields. The skunky, berry flavors will capture your senses while the cerebral, uplifting effects provide an aura of euphoria that is sure to leave a smile on your face. Strawberry Cough is a great solution in times of elevated stress.$$,
    leafly_rating = 4.32577040298002,
    leafly_review_count = 2953,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Haze","Strawberry Fields"}'::TEXT[],
    lineage = $$Haze x Strawberry Fields$$,
    image_url = 'https://images.leafly.com/flower-images/strawberry-cough.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/strawberry-cough',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%strawberry%cough%');



-- Update products for: Mimosa
UPDATE products
SET
    leafly_strain_type = 'Hybrid',
    leafly_description = $$Mimosa, also known as "Purple Mimosa," is ahybrid marijuana strainmade by crossingClementinewithPurple Punch. In small doses, this strain produceshappy, level-headed effects that will leave you feelingupliftedand motivated enough to take on any mundane task. In large doses, Mimosa may make you feelsleepyandrelaxed. This strain has a strong aroma and flavor that reminds you of its namesake, with notes offruitandcitrusflavors bursting through. Medical marijuana patients choose this strain to help relieve symptoms associated withdepressionandstress. Mimosa is a staple from theTangiefamily. Breeder Symbiotic Genetics has released a refined Mimosa dubbed Mimosa v6.$$,
    leafly_rating = 4.435875216637782,
    leafly_review_count = 1154,
    effects = '{"Relaxed","Aroused","Tingly","Euphoric","Happy","Uplifted","Energetic","Creative","Focused","Giggly","Sleepy","Hungry","Talkative","Calm"}'::TEXT[],
    helps_with = '{"Anxiety","Stress","Depression","Pain","Insomnia","Fatigue","Lack of appetite","Nausea","Inflammation","Muscle spasms","Migraines","Headaches","Cramps","PTSD"}'::TEXT[],
    negatives = '{"Dry mouth","Dry eyes","Paranoid","Anxious","Dizzy","Headache"}'::TEXT[],
    flavors = '{"Lavender","Pepper","Flowery","Earthy","Pine","Diesel","Citrus","Lemon","Berry","Grape","Sweet","Spicy","Mint","Vanilla","Butter","Tropical","Woody","Pungent","Skunk","Chemical","Ammonia","Tree Fruit","Apple","Apricot","Peach","Pear","Orange","Grapefruit","Blueberry","Strawberry","Cheese","Tar","Tobacco","Menthol","Nutty","Coffee","Tea","Honey","Rose","Violet"}'::TEXT[],
    terpenes = '{"Caryophyllene","Limonene","Myrcene","Linalool","Pinene","Humulene","Terpinolene","Ocimene"}'::TEXT[],
    parent_strains = '{"Clementine","Purple Punch"}'::TEXT[],
    lineage = $$Clementine x Purple Punch$$,
    image_url = 'https://leafly-public.imgix.net/strains/photos/sE4UZNIUQbSxoqEEk0E1_Mimosa.png?auto=compress&w=1200&h=630&fit=crop&bg=FFFFFF&fit=fill',
    leafly_url = 'https://www.leafly.com/strains/mimosa',
    leafly_data_updated_at = NOW()
WHERE
    leafly_description IS NULL
    AND (name ILIKE '%mimosa%');




COMMIT;