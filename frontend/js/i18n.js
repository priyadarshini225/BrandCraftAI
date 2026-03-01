/**
 * i18n.js — BizForge / BrandPilot AI
 * Lightweight client-side internationalisation module.
 * Supported: English (en), Spanish (es), French (fr), German (de), Hindi (hi)
 */

const TRANSLATIONS = {
  en: {
    nav_features: "Features",
    nav_studio: "Studio",
    nav_about: "About",
    hero_title: "Build Your Brand with AI",
    hero_subtitle: "Create stunning brand names, logos, marketing content, and complete design systems in seconds",
    hero_cta: "Launch AI Studio \u2192",
    feature_brand_names: "Brand Names",
    feature_brand_names_desc: "Generate 10 creative, domain-friendly brand name ideas for your industry.",
    feature_logo: "Logo Studio",
    feature_logo_desc: "Generate professional, vector-quality logos instantly with Stable Diffusion XL.",
    feature_marketing: "Marketing Content",
    feature_marketing_desc: "Taglines, social posts, email campaigns & product descriptions \u2014 compelling copy at scale.",
    feature_design: "Brand Kit",
    feature_design_desc: "Complete brand system: color palettes, typography pairs, and social mockups auto-generated.",
    feature_sentiment: "Sentiment Analysis",
    feature_sentiment_desc: "Evaluate taglines and copy with AI-powered brand analysis. Know how your message lands.",
    feature_chat: "AI Consultant",
    feature_chat_desc: "Refine your brand strategy, voice, and positioning with your personal AI consultant.",
    feature_logo_cta: "Try Generator \u2192",
    feature_design_cta: "View Samples \u2192",
    feature_chat_cta: "Start Chatting \u2192",
    feature_brand_names_cta: "Explore Names \u2192",
    feature_marketing_cta: "Create Content \u2192",
    feature_sentiment_cta: "Analyze Now \u2192",
    ctx_badge: "AI Feature",
    why_heading: "Why Choose BizForge?",
    why_ai: "AI-Powered Tools",
    why_instant: "Instant Results",
    why_multi: "Multilingual",
    why_voice: "Voice Input",
    why_pro: "Professional Output",
    footer_text: "\u00a9 2026 BizForge \u2014 Powered by IBM Granite, Groq AI & Stable Diffusion XL",
    loading: "AI is creating your brand...",
    copy: "Copy",
    copied: "Copied!",
    generate: "Generate",
    studio_title: "Brand Parameters",
    studio_subtitle: "Define your brand essence below",
    tab_names: "Names",
    tab_logo: "Logo",
    tab_copy: "Content",
    tab_design: "Design",
    tab_analysis: "Analysis",
    tab_chat: "Chat",
    gen_brand_names: "Generate Brand Names",
    gen_logo: "Generate Logo",
    gen_content: "Generate Content",
    gen_posts: "Generate Content",
    gen_desc: "Generate Description",
    hero_line1: "Build Your Brand",
    hero_cta_start: "Start Creating \u2192",
    footer_copy: "\u00a9 2026 BrandCraft AI. All rights reserved.",
  },
  es: {
    nav_features: "Funciones",
    nav_studio: "Estudio",
    nav_about: "Acerca de",
    hero_title: "Construye tu Marca con IA",
    hero_subtitle: "Crea nombres de marca, logos, contenido de marketing y sistemas de dise\u00f1o completos en segundos",
    hero_cta: "Iniciar Estudio de IA \u2192",
    feature_brand_names: "Nombres de Marca",
    feature_brand_names_desc: "Genera 10 ideas creativas de nombres de marca para tu industria.",
    feature_logo: "Estudio de Logos",
    feature_logo_desc: "Genera logos profesionales al instante con Stable Diffusion XL.",
    feature_marketing: "Contenido de Marketing",
    feature_marketing_desc: "Slogans, publicaciones sociales, campa\u00f1as de email y descripciones de productos.",
    feature_design: "Kit de Marca",
    feature_design_desc: "Sistema de marca completo: paletas de color, tipograf\u00edas y mockups autogenerados.",
    feature_sentiment: "An\u00e1lisis de Sentimiento",
    feature_sentiment_desc: "Eval\u00faa tus slogans con an\u00e1lisis de marca impulsado por IA.",
    feature_chat: "Consultor IA",
    feature_chat_desc: "Refina tu estrategia de marca con tu consultor de IA personal.",
    feature_logo_cta: "Probar Generador \u2192",
    feature_design_cta: "Ver Muestras \u2192",
    feature_chat_cta: "Comenzar Chat \u2192",
    feature_brand_names_cta: "Explorar Nombres \u2192",
    feature_marketing_cta: "Crear Contenido \u2192",
    feature_sentiment_cta: "Analizar Ahora \u2192",
    ctx_badge: "Funci\u00f3n IA",
    why_heading: "\u00bfPor qu\u00e9 BizForge?",
    why_ai: "Herramientas IA",
    why_instant: "Resultados Instant\u00e1neos",
    why_multi: "Multing\u00fce",
    why_voice: "Entrada de Voz",
    why_pro: "Salida Profesional",
    footer_text: "\u00a9 2026 BizForge \u2014 Impulsado por IBM Granite, Groq AI y Stable Diffusion XL",
    loading: "La IA est\u00e1 creando tu marca...",
    copy: "Copiar",
    copied: "\u00a1Copiado!",
    generate: "Generar",
    studio_title: "Par\u00e1metros de Marca",
    studio_subtitle: "Define la esencia de tu marca",
    tab_names: "Nombres",
    tab_logo: "Logo",
    tab_copy: "Contenido",
    tab_design: "Dise\u00f1o",
    tab_analysis: "An\u00e1lisis",
    tab_chat: "Chat",
    gen_brand_names: "Generar Nombres de Marca",
    gen_logo: "Generar Logo",
    gen_content: "Generar Contenido",
    gen_posts: "Generar Posts",
    gen_desc: "Generar Descripci\u00f3n",
    hero_line1: "Construye tu Marca",
    hero_cta_start: "Comenzar a Crear \u2192",
    footer_copy: "\u00a9 2026 BrandCraft AI. Todos los derechos reservados.",
  },
  fr: {
    nav_features: "Fonctionnalit\u00e9s",
    nav_studio: "Studio",
    nav_about: "\u00c0 propos",
    hero_title: "Construisez votre Marque avec l'IA",
    hero_subtitle: "Cr\u00e9ez des noms de marque, logos, contenus marketing et syst\u00e8mes de design en quelques secondes",
    hero_cta: "Lancer le Studio IA \u2192",
    feature_brand_names: "Noms de Marque",
    feature_brand_names_desc: "G\u00e9n\u00e9rez 10 id\u00e9es cr\u00e9atives de noms de marque pour votre secteur.",
    feature_logo: "Studio de Logos",
    feature_logo_desc: "G\u00e9n\u00e9rez des logos professionnels instantan\u00e9ment avec Stable Diffusion XL.",
    feature_marketing: "Contenu Marketing",
    feature_marketing_desc: "Slogans, posts, campagnes e-mail et descriptions de produits \u2014 \u00e0 grande \u00e9chelle.",
    feature_design: "Kit de Marque",
    feature_design_desc: "Syst\u00e8me de marque complet: palettes, typographies et mockups autog\u00e9n\u00e9r\u00e9s.",
    feature_sentiment: "Analyse de Sentiment",
    feature_sentiment_desc: "\u00c9valuez vos slogans avec l'analyse de marque IA.",
    feature_chat: "Consultant IA",
    feature_chat_desc: "Affinez votre strat\u00e9gie de marque avec votre consultant IA personnel.",
    feature_logo_cta: "Essayer le G\u00e9n\u00e9rateur \u2192",
    feature_design_cta: "Voir les Exemples \u2192",
    feature_chat_cta: "D\u00e9marrer le Chat \u2192",
    feature_brand_names_cta: "Explorer les Noms \u2192",
    feature_marketing_cta: "Cr\u00e9er du Contenu \u2192",
    feature_sentiment_cta: "Analyser Maintenant \u2192",
    ctx_badge: "Fonctionnalit\u00e9 IA",
    why_heading: "Pourquoi BizForge?",
    why_ai: "Outils IA",
    why_instant: "R\u00e9sultats Instantan\u00e9s",
    why_multi: "Multilingue",
    why_voice: "Entr\u00e9e Vocale",
    why_pro: "Sortie Professionnelle",
    footer_text: "\u00a9 2026 BizForge \u2014 Propuls\u00e9 par IBM Granite, Groq AI et Stable Diffusion XL",
    loading: "L'IA cr\u00e9e votre marque...",
    copy: "Copier",
    copied: "Copi\u00e9!",
    generate: "G\u00e9n\u00e9rer",
    studio_title: "Param\u00e8tres de Marque",
    studio_subtitle: "D\u00e9finissez l'essence de votre marque",
    tab_names: "Noms",
    tab_logo: "Logo",
    tab_copy: "Contenu",
    tab_design: "Design",
    tab_analysis: "Analyse",
    tab_chat: "Chat",
    gen_brand_names: "G\u00e9n\u00e9rer des Noms de Marque",
    gen_logo: "G\u00e9n\u00e9rer un Logo",
    gen_content: "G\u00e9n\u00e9rer du Contenu",
    gen_posts: "G\u00e9n\u00e9rer des Posts",
    gen_desc: "G\u00e9n\u00e9rer une Description",
    hero_line1: "Construisez votre Marque",
    hero_cta_start: "Commencer \u00e0 Cr\u00e9er \u2192",
    footer_copy: "\u00a9 2026 BrandCraft AI. Tous droits r\u00e9serv\u00e9s.",
  },
  de: {
    nav_features: "Funktionen",
    nav_studio: "Studio",
    nav_about: "\u00dcber uns",
    hero_title: "Baue deine Marke mit KI",
    hero_subtitle: "Erstelle in Sekunden Markennamen, Logos, Marketing-Inhalte und komplette Design-Systeme",
    hero_cta: "KI-Studio starten \u2192",
    feature_brand_names: "Markennamen",
    feature_brand_names_desc: "Generiere 10 kreative Markenname-Ideen f\u00fcr deine Branche.",
    feature_logo: "Logo-Studio",
    feature_logo_desc: "Erstelle professionelle Logos sofort mit Stable Diffusion XL.",
    feature_marketing: "Marketing-Inhalte",
    feature_marketing_desc: "Slogans, Social Posts, E-Mail-Kampagnen und Produktbeschreibungen \u2014 in gro\u00dfem Ma\u00dfstab.",
    feature_design: "Marken-Kit",
    feature_design_desc: "Vollst\u00e4ndiges Markensystem: Farbpaletten, Typografien und Mockups automatisch generiert.",
    feature_sentiment: "Sentiment-Analyse",
    feature_sentiment_desc: "Bewerte deine Slogans mit KI-gest\u00fctzter Markenanalyse.",
    feature_chat: "KI-Berater",
    feature_chat_desc: "Verfeinere deine Markenstrategie mit deinem pers\u00f6nlichen KI-Berater.",
    feature_logo_cta: "Generator starten \u2192",
    feature_design_cta: "Beispiele ansehen \u2192",
    feature_chat_cta: "Chat beginnen \u2192",
    feature_brand_names_cta: "Namen erkunden \u2192",
    feature_marketing_cta: "Inhalt erstellen \u2192",
    feature_sentiment_cta: "Jetzt analysieren \u2192",
    ctx_badge: "KI-Funktion",
    why_heading: "Warum BizForge?",
    why_ai: "KI-Tools",
    why_instant: "Sofortergebnisse",
    why_multi: "Mehrsprachig",
    why_voice: "Spracheingabe",
    why_pro: "Professionelle Ausgabe",
    footer_text: "\u00a9 2026 BizForge \u2014 Betrieben von IBM Granite, Groq AI & Stable Diffusion XL",
    loading: "KI erstellt deine Marke...",
    copy: "Kopieren",
    copied: "Kopiert!",
    generate: "Generieren",
    studio_title: "Markenparameter",
    studio_subtitle: "Definiere die Essenz deiner Marke",
    tab_names: "Namen",
    tab_logo: "Logo",
    tab_copy: "Inhalt",
    tab_design: "Design",
    tab_analysis: "Analyse",
    tab_chat: "Chat",
    gen_brand_names: "Markennamen generieren",
    gen_logo: "Logo generieren",
    gen_content: "Inhalt generieren",
    gen_posts: "Posts generieren",
    gen_desc: "Beschreibung generieren",
    hero_line1: "Baue deine Marke auf",
    hero_cta_start: "Jetzt starten \u2192",
    footer_copy: "\u00a9 2026 BrandCraft AI. Alle Rechte vorbehalten.",
  },
  hi: {
    nav_features: "\u0938\u0941\u0935\u093f\u0927\u093e\u090f\u0902",
    nav_studio: "\u0938\u094d\u091f\u0942\u0921\u093f\u092f\u094b",
    nav_about: "\u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902",
    hero_title: "AI \u0938\u0947 \u0905\u092a\u0928\u093e \u092c\u094d\u0930\u093e\u0902\u0921 \u092c\u0928\u093e\u090f\u0902",
    hero_subtitle: "\u0938\u0947\u0915\u0902\u0921\u094b\u0902 \u092e\u0947\u0902 \u0936\u093e\u0928\u0926\u093e\u0930 \u092c\u094d\u0930\u093e\u0902\u0921 \u0928\u093e\u092e, \u0932\u094b\u0917\u094b, \u092e\u093e\u0930\u094d\u0915\u0947\u091f\u093f\u0902\u0917 \u0938\u093e\u092e\u0917\u094d\u0930\u0940 \u0914\u0930 \u0921\u093f\u091c\u093c\u093e\u0907\u0928 \u0938\u093f\u0938\u094d\u091f\u092e \u092c\u0928\u093e\u090f\u0902",
    hero_cta: "AI \u0938\u094d\u091f\u0942\u0921\u093f\u092f\u094b \u0932\u0949\u0928\u094d\u091a \u0915\u0930\u0947\u0902 \u2192",
    feature_brand_names: "\u092c\u094d\u0930\u093e\u0902\u0921 \u0928\u093e\u092e",
    feature_brand_names_desc: "\u0905\u092a\u0928\u0947 \u0909\u0926\u094d\u092f\u094b\u0917 \u0915\u0947 \u0932\u093f\u090f 10 \u0930\u091a\u0928\u093e\u0924\u094d\u092e\u0915 \u092c\u094d\u0930\u093e\u0902\u0921 \u0928\u093e\u092e \u0935\u093f\u091a\u093e\u0930 \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902\u0964",
    feature_logo: "\u0932\u094b\u0917\u094b \u0938\u094d\u091f\u0942\u0921\u093f\u092f\u094b",
    feature_logo_desc: "Stable Diffusion XL \u0938\u0947 \u0924\u0941\u0930\u0902\u0924 \u092a\u0947\u0936\u0947\u0935\u0930 \u0932\u094b\u0917\u094b \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902\u0964",
    feature_marketing: "\u092e\u093e\u0930\u094d\u0915\u0947\u091f\u093f\u0902\u0917 \u0938\u093e\u092e\u0917\u094d\u0930\u0940",
    feature_marketing_desc: "\u091f\u0948\u0917\u0932\u093e\u0907\u0928, \u0938\u094b\u0936\u0932 \u092a\u094b\u0938\u094d\u091f, \u0908\u092e\u0947\u0932 \u0915\u0948\u0902\u092a\u0947\u0928 \u0914\u0930 \u0909\u0924\u094d\u092a\u093e\u0926 \u0935\u093f\u0935\u0930\u0923 \u092c\u0928\u093e\u090f\u0902\u0964",
    feature_design: "\u092c\u094d\u0930\u093e\u0902\u0921 \u0915\u093f\u091f",
    feature_design_desc: "\u092a\u0942\u0930\u094d\u0923 \u092c\u094d\u0930\u093e\u0902\u0921 \u0938\u093f\u0938\u094d\u091f\u092e: \u0930\u0902\u0917 \u092a\u0948\u0932\u0947\u091f, \u091f\u093e\u0907\u092a\u094b\u0917\u094d\u0930\u093e\u092b\u0940 \u0914\u0930 \u092e\u0949\u0915\u0905\u092a \u0938\u094d\u0935\u091a\u093e\u0932\u093f\u0924 \u0905\u0928\u0941\u0935\u093e\u0926\u093f\u0924\u0964",
    feature_sentiment: "\u092d\u093e\u0935\u0928\u093e \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923",
    feature_sentiment_desc: "AI-\u0938\u0902\u091a\u093e\u0932\u093f\u0924 \u092c\u094d\u0930\u093e\u0902\u0921 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u0938\u0947 \u0905\u092a\u0928\u0940 \u091f\u0948\u0917\u0932\u093e\u0907\u0928 \u0915\u093e \u092e\u0942\u0932\u094d\u092f\u093e\u0902\u0915\u0928 \u0915\u0930\u0947\u0902\u0964",
    feature_chat: "AI \u0938\u0932\u093e\u0939\u0915\u093e\u0930",
    feature_chat_desc: "\u0905\u092a\u0928\u0947 \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0917\u0924 AI \u0938\u0932\u093e\u0939\u0915\u093e\u0930 \u0915\u0947 \u0938\u093e\u0925 \u092c\u094d\u0930\u093e\u0902\u0921 \u0930\u0923\u0928\u0940\u0924\u093f \u0938\u0941\u0927\u093e\u0930\u0947\u0902\u0964",
    feature_logo_cta: "\u091c\u0947\u0928\u0930\u0947\u091f\u0930 \u0906\u091c\u092e\u093e\u090f\u0902 \u2192",
    feature_design_cta: "\u0928\u092e\u0942\u0928\u0947 \u0926\u0947\u0916\u0947\u0902 \u2192",
    feature_chat_cta: "\u091a\u0948\u091f \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902 \u2192",
    feature_brand_names_cta: "\u0928\u093e\u092e \u0916\u094b\u091c\u0947\u0902 \u2192",
    feature_marketing_cta: "\u0938\u093e\u092e\u0917\u094d\u0930\u0940 \u092c\u0928\u093e\u090f\u0902 \u2192",
    feature_sentiment_cta: "\u0905\u092d\u0940 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u0915\u0930\u0947\u0902 \u2192",
    ctx_badge: "AI \u0938\u0941\u0935\u093f\u0927\u093e",
    why_heading: "BizForge \u0915\u094d\u092f\u094b\u0902 \u091a\u0941\u0928\u0947\u0902?",
    why_ai: "AI-\u0938\u0902\u091a\u093e\u0932\u093f\u0924 \u091f\u0942\u0932",
    why_instant: "\u0924\u0924\u094d\u0915\u093e\u0932 \u092a\u0930\u093f\u0923\u093e\u092e",
    why_multi: "\u092c\u0939\u0941\u092d\u093e\u0937\u0940",
    why_voice: "\u0935\u0949\u092f\u0938 \u0907\u0928\u092a\u0941\u091f",
    why_pro: "\u092a\u0947\u0936\u0947\u0935\u0930 \u0906\u0909\u091f\u092a\u0941\u091f",
    footer_text: "\u00a9 2026 BizForge \u2014 IBM Granite, Groq AI \u0914\u0930 Stable Diffusion XL \u0926\u094d\u0935\u093e\u0930\u093e \u0938\u0902\u091a\u093e\u0932\u093f\u0924",
    loading: "AI \u0906\u092a\u0915\u093e \u092c\u094d\u0930\u093e\u0902\u0921 \u092c\u0928\u093e \u0930\u0939\u093e \u0939\u0948...",
    copy: "\u0915\u0949\u092a\u0940 \u0915\u0930\u0947\u0902",
    copied: "\u0915\u0949\u092a\u0940 \u0939\u094b \u0917\u092f\u093e!",
    generate: "\u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    studio_title: "\u092c\u094d\u0930\u093e\u0902\u0921 \u092a\u0948\u0930\u093e\u092e\u0940\u091f\u0930",
    studio_subtitle: "\u0905\u092a\u0928\u0947 \u092c\u094d\u0930\u093e\u0902\u0921 \u0915\u0940 \u092a\u0939\u091a\u093e\u0928 \u092a\u0930\u093f\u092d\u093e\u0937\u093f\u0924 \u0915\u0930\u0947\u0902",
    tab_names: "\u0928\u093e\u092e",
    tab_logo: "\u0932\u094b\u0917\u094b",
    tab_copy: "\u0915\u0949\u092a\u0940",
    tab_design: "\u0921\u093f\u091c\u093c\u093e\u0907\u0928",
    tab_analysis: "\u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923",
    tab_chat: "\u091a\u0948\u091f",
    gen_brand_names: "\u092c\u094d\u0930\u093e\u0902\u0921 \u0928\u093e\u092e \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    gen_logo: "\u0932\u094b\u0917\u094b \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    gen_content: "\u0938\u093e\u092e\u0917\u094d\u0930\u0940 \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    gen_posts: "\u092a\u094b\u0938\u094d\u091f \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    gen_desc: "\u0935\u093f\u0935\u0930\u0923 \u091c\u0947\u0928\u0930\u0947\u091f \u0915\u0930\u0947\u0902",
    hero_line1: "\u0905\u092a\u0928\u093e \u092c\u094d\u0930\u093e\u0902\u0921 \u092c\u0928\u093e\u090f\u0902",
    hero_cta_start: "\u092c\u0928\u093e\u0928\u093e \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902 \u2192",
    footer_copy: "\u00a9 2026 BrandCraft AI. \u0938\u0930\u094d\u0935\u093e\u0927\u093f\u0915\u093e\u0930 \u0938\u0941\u0930\u0915\u094d\u0937\u093f\u0924\u0964",
  },
};
let currentLang = "en";

/**
 * Apply all [data-i18n] and [data-i18n-placeholder] text in the DOM.
 * Dispatches a 'langchange' custom event so other JS can react.
 */
function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) return;
  currentLang = lang;
  const dict = TRANSLATIONS[lang];

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] !== undefined) el.textContent = dict[key];
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key] !== undefined) el.placeholder = dict[key];
  });

  document.documentElement.lang = lang;
  localStorage.setItem("bizforge_lang", lang);

  // Let other scripts react to the language change
  window.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

/**
 * Translate a single key using the current language, fallback to English.
 */
function translate(key) {
  return (TRANSLATIONS[currentLang] || {})[key]
    || (TRANSLATIONS["en"] || {})[key]
    || key;
}
// Keep 't' as an alias for backward compat
const t = translate;

// ── Robust initialisation ─────────────────────────────────────────────────────
// Works whether DOMContentLoaded has already fired or not (handles bfcache, defer, etc.)
function _initI18n() {
  const saved = localStorage.getItem("bizforge_lang") || "en";
  const selector = document.getElementById("lang-selector");
  if (selector) {
    selector.value = saved;
    selector.addEventListener("change", (e) => setLanguage(e.target.value));
  }
  setLanguage(saved);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", _initI18n);
} else {
  // DOM already ready (script loaded late / bfcache restore)
  _initI18n();
}
