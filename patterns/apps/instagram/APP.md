---
version: 1
app: Instagram
spotlight_name: Instagram
icon: ◎
locale: fr_CA
archetype: social-feed
reset_before_explore: true
obstacle_mode: auto
---

# Instagram

## Structure

Social feed app with 5 bottom tabs: Accueil, Recherche, Reels, Boutique, Profil.
The top-right corner of Accueil has DM (paper plane) and notifications (heart) icons.

## Accueil Tab (Home)
- Top row: Instagram logo (left), Heart notifications icon, DM paper plane icon (right)
- Stories bar below header: horizontal scroll of avatar circles — AUTO-ADVANCE, avoid tapping
- Full posts below stories: avatar, username, image, caption, like/comment/share
- Infinite scroll — do NOT scroll through posts
- Tap username or avatar to visit a profile

## Search Tab
- Search bar at top
- Grid of explore images below
- Tap a post to view in detail
- Tap search bar to type a query

## Reels Tab
- Full-screen video feed (like TikTok)
- Swipe up for next reel (NOT tap)
- Right-side engagement icons: like, comment, share, save

## Profile Tab
- User profile header: avatar, name, follower counts
- Bio text
- Post grid below (3-column)
- Tabs for Posts, Reels, Tagged
- Settings (three lines icon) in top-right

## Obstacles
- iPhone camera is not available → tap "OK"
- Login prompt → tap "Fermer"
- Notification permission → tap "Ne pas autoriser"
- Activer les notifications → tap "Pas maintenant"
- PUBLICATION STORY → tap "X"
- Tagged in photo prompt → tap "X"
- Story viewer overlay → tap "X"

## Skip
- Supprimer
- Supprimer le compte
- Se déconnecter
- Publier
- Republier
- Bloquer
- Signaler
- Votre story
- Aimé par
- J'aime
- Suggestions
- Voir la traduction
- commentaire
- Abonné
- Plus tard
- Télécharger sur l'App Store
- Rejoindre avec Instagram
- /et \d+ autres/

## Deep Tabs
- Profil

## Tips
- Accueil feed is infinite — navigate exclusively via bottom tabs
- Recherche tab has the richest discovery structure
- Profil tab → Settings gear reveals the deepest navigation
- DM icon (top-right, paper plane) opens messaging — separate navigation tree
- Heart icon (top-right) opens notifications
- Stories bar at top of Accueil auto-advances and triggers camera — NEVER tap story avatars
- Tapping usernames in posts may open camera/story overlays on test devices
- If the camera dialog appears, it's because an avatar/story was tapped — dismiss with "OK"

## Simulator
- root: accueil
- tab_bar_style: icons

## Simulator Screen accueil
- title: Accueil
- back: null
- tab_bar: true
- element text: "@johndoe"
- element text: "Belle journée à la plage"
- element text: "@janesmithphoto"
- element text: "Café et code"
- element tab: "Accueil" → accueil
- element tab: "Recherche" → recherche
- element tab: "Reels" → reels
- element tab: "Boutique" → boutique
- element tab: "Profil" → profil_ig

## Simulator Screen recherche
- title: Recherche
- back: null
- tab_bar: true
- element row: "Voyage" → voyage_ig
- element row: "Mode" → mode
- element row: "Photographie" → photographie
- element tab: "Accueil" → accueil
- element tab: "Recherche" → recherche
- element tab: "Reels" → reels
- element tab: "Boutique" → boutique
- element tab: "Profil" → profil_ig

## Simulator Screen voyage_ig
- title: Voyage
- back: recherche
- element text: "Destinations populaires"

## Simulator Screen mode
- title: Mode
- back: recherche
- element text: "Tendances mode"

## Simulator Screen photographie
- title: Photographie
- back: recherche
- element text: "Photographes à suivre"

## Simulator Screen reels
- title: Reels
- back: null
- tab_bar: true
- element text: "Vidéo en lecture"
- element tab: "Accueil" → accueil
- element tab: "Recherche" → recherche
- element tab: "Reels" → reels
- element tab: "Boutique" → boutique
- element tab: "Profil" → profil_ig

## Simulator Screen boutique
- title: Boutique
- back: null
- tab_bar: true
- element row: "Mode" → mode_shop
- element row: "Beauté" → beaute_shop
- element tab: "Accueil" → accueil
- element tab: "Recherche" → recherche
- element tab: "Reels" → reels
- element tab: "Boutique" → boutique
- element tab: "Profil" → profil_ig

## Simulator Screen mode_shop
- title: Mode
- back: boutique
- element text: "Produits mode"

## Simulator Screen beaute_shop
- title: Beauté
- back: boutique
- element text: "Produits de beauté"

## Simulator Screen profil_ig
- title: Profil
- back: null
- tab_bar: true
- element text: "Photographer & traveler"
- element text: "42 publications"
- element text: "1.2K abonnés"
- element text: "890 abonnements"
- element row: "Paramètres" → parametres_ig
- element tab: "Accueil" → accueil
- element tab: "Recherche" → recherche
- element tab: "Reels" → reels
- element tab: "Boutique" → boutique
- element tab: "Profil" → profil_ig

## Simulator Screen parametres_ig
- title: Paramètres
- back: profil_ig
- element row: "Compte" → compte_ig
- element row: "Notifications" → notif_ig
- element row: "Confidentialité" → confidentialite_ig

## Simulator Screen compte_ig
- title: Compte
- back: parametres_ig
- element text: "Informations personnelles"

## Simulator Screen notif_ig
- title: Notifications
- back: parametres_ig
- element text: "Mentions et tags"

## Simulator Screen confidentialite_ig
- title: Confidentialité
- back: parametres_ig
- element text: "Compte privé"

## Simulator Obstacle camera
- title: "iPhone camera is not available"
- buttons: OK
- trigger: never

## Simulator Obstacle login_ig
- title: "Connectez-vous à Instagram"
- body: "Découvrez ce que font vos amis"
- buttons: Se connecter, Fermer
- trigger: on_first_describe

## Simulator Obstacle notif_perm
- title: "Activer les notifications?"
- buttons: Activer, Pas maintenant
- trigger: after_n_taps:3
