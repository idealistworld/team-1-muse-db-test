BEGIN;

-- 1) USER PROFILES (parents)
INSERT INTO public.user_profiles (user_id, subscription_tier, created_at, updated_at) VALUES
('6d31c637-dd42-4a44-a0a4-ba9eda5dfebf', 'free',  '2025-10-05 21:35:25.97172+00', '2025-10-05 21:35:25.97172+00'),
('71fd4d4b-ad95-4d77-8e43-5d0d666a5693', 'pro',   '2025-10-05 20:49:05.269117+00','2025-10-05 20:49:05.269117+00'),
('f08c2ad0-7629-4da6-ab99-44a7ad32a3e2', 'free',  '2025-10-05 21:35:25.97172+00', '2025-10-05 21:35:25.97172+00')
ON CONFLICT (user_id) DO NOTHING;

-- 2) CREATOR PROFILES (parents) — idempotent via WHERE NOT EXISTS (no identity values)
INSERT INTO public.creator_profiles (profile_url, platform, created_at, updated_at)
SELECT 'https://www.linkedin.com/in/josephalalou/', 'linkedin',
       '2025-10-05 21:10:07.089567+00', '2025-10-05 21:48:11.548905+00'
WHERE NOT EXISTS (
  SELECT 1 FROM public.creator_profiles
  WHERE lower(platform)='linkedin'
    AND lower(profile_url)='https://www.linkedin.com/in/josephalalou/'
);

INSERT INTO public.creator_profiles (profile_url, platform, created_at, updated_at)
SELECT 'https://www.linkedin.com/in/robin-guo/', 'linkedin',
       '2025-10-05 21:40:23.852761+00', '2025-10-05 21:55:34.986191+00'
WHERE NOT EXISTS (
  SELECT 1 FROM public.creator_profiles
  WHERE lower(platform)='linkedin'
    AND lower(profile_url)='https://www.linkedin.com/in/robin-guo/'
);

INSERT INTO public.creator_profiles (profile_url, platform, created_at, updated_at)
SELECT 'https://www.linkedin.com/in/ryan/', 'linkedin',
       '2025-10-05 21:40:23.852761+00', '2025-10-05 21:48:17.183156+00'
WHERE NOT EXISTS (
  SELECT 1 FROM public.creator_profiles
  WHERE lower(platform)='linkedin'
    AND lower(profile_url)='https://www.linkedin.com/in/ryan/'
);

-- 3) CREATOR CONTENT (child of creator_profiles) — de-dupe via NOT EXISTS (no content_id column)
INSERT INTO public.creator_content (creator_id, post_url, post_raw, created_at, updated_at)
SELECT cp.creator_id,
       'https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/',
       'Whenever I speak with college students I try to instill the urgency of the market ... Go make something. Because the window is short and your time finite.',
       '2025-10-05 21:53:01.781105+00',
       '2025-10-05 21:53:01.781105+00'
FROM public.creator_profiles cp
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/robin-guo/'
  AND NOT EXISTS (
        SELECT 1 FROM public.creator_content cc
        WHERE cc.creator_id = cp.creator_id
          AND cc.post_url = 'https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/'
  );

INSERT INTO public.creator_content (creator_id, post_url, post_raw, created_at, updated_at)
SELECT cp.creator_id,
       'https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/',
       'Being an engineer or “being technical” is, at its core, understanding deeply how something works...',
       '2025-10-05 21:56:06.719606+00',
       '2025-10-05 21:56:06.719606+00'
FROM public.creator_profiles cp
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/robin-guo/'
  AND NOT EXISTS (
        SELECT 1 FROM public.creator_content cc
        WHERE cc.creator_id = cp.creator_id
          AND cc.post_url = 'https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/'
  );

-- 4) USER POSTS (child of user_profiles)
INSERT INTO public.user_posts (post_id, user_id, raw_text, created_at, updated_at) VALUES
('0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9', '6d31c637-dd42-4a44-a0a4-ba9eda5dfebf', 'If you consider yourself an engineer...', '2025-10-05 21:44:37.966178+00', '2025-10-05 21:44:37.966178+00'),
('8a845cc5-77f7-4a00-883b-e277b73a4ebb', 'f08c2ad0-7629-4da6-ab99-44a7ad32a3e2', 'I don''t need any inspiration for my post because it''s just a cute dog!', '2025-10-05 21:44:52.00489+00', '2025-10-05 21:44:52.00489+00'),
('e037dfd2-5e20-458c-8179-2289c23a42ea', '71fd4d4b-ad95-4d77-8e43-5d0d666a5693', 'When I reflect on the positions of my peers...', '2025-10-05 21:45:16.451121+00', '2025-10-05 21:45:16.451121+00')
ON CONFLICT (post_id) DO NOTHING;

-- 5) USER MEDIA (child of user_posts)
INSERT INTO public.user_media (user_media_id, post_id, media_url, media_type, created_at, updated_at) VALUES
('bdd7ab64-8633-417b-8068-0830d7c97fc8', '8a845cc5-77f7-4a00-883b-e277b73a4ebb', 'https://petcube.com/blog/content/images/2018/04/boo-the-dog-2.jpg', 'image', '2025-10-05 21:46:08.867377+00', '2025-10-05 21:46:08.867377+00')
ON CONFLICT (user_media_id) DO NOTHING;

-- 6) USER FOLLOWS (child of user_profiles & creator_profiles) — lookup creator_id
INSERT INTO public.user_follows (id, user_id, creator_id, created_at)
SELECT '4dfdadd3-104e-4472-b5c0-35b5445be233',
       '71fd4d4b-ad95-4d77-8e43-5d0d666a5693',
       cp.creator_id,
       '2025-10-05 21:51:44.075097+00'
FROM public.creator_profiles cp
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/robin-guo/'
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.user_follows (id, user_id, creator_id, created_at)
SELECT '68c31ebd-9f75-466d-b062-fdbcdff50037',
       '71fd4d4b-ad95-4d77-8e43-5d0d666a5693',
       cp.creator_id,
       '2025-10-05 21:51:31.144221+00'
FROM public.creator_profiles cp
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/ryan/'
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.user_follows (id, user_id, creator_id, created_at)
SELECT 'f07f3fe1-9f7f-4e51-b923-d8da806c8469',
       '6d31c637-dd42-4a44-a0a4-ba9eda5dfebf',
       cp.creator_id,
       '2025-10-05 21:51:20.860184+00'
FROM public.creator_profiles cp
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/ryan/'
ON CONFLICT (id) DO NOTHING;

-- 7) POST INSPIRATIONS (leaf; child of user_posts & creator_content)
INSERT INTO public.post_inspirations (post_id, content_id, created_at, updated_at)
SELECT '0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9',
       cc.content_id,
       '2025-10-05 21:57:41.227074+00'::timestamptz,
       '2025-10-05 21:57:41.227074+00'::timestamptz
FROM public.creator_content cc
JOIN public.creator_profiles cp ON cp.creator_id = cc.creator_id
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/robin-guo/'
  AND cc.post_url='https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/'
ON CONFLICT ON CONSTRAINT post_inspirations_unique DO NOTHING;

INSERT INTO public.post_inspirations (post_id, content_id, created_at, updated_at)
SELECT 'e037dfd2-5e20-458c-8179-2289c23a42ea',
       cc.content_id,
       '2025-10-05 22:01:46.447934+00'::timestamptz,
       '2025-10-05 22:01:46.447934+00'::timestamptz
FROM public.creator_content cc
JOIN public.creator_profiles cp ON cp.creator_id = cc.creator_id
WHERE lower(cp.platform)='linkedin'
  AND lower(cp.profile_url)='https://www.linkedin.com/in/robin-guo/'
  AND cc.post_url='https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/'
ON CONFLICT ON CONSTRAINT post_inspirations_unique DO NOTHING;

COMMIT;
