/*
 * Centralised translation system
 *  - TRANSLATIONS dictionary (en / es / hi)
 *  - t(key)            -> returns translated string for current lang
 *  - translatePage()   -> walks every [data-key] element and localises it
 *  - initLanguageSelect() -> wires up the <select#languageSelect> dropdown
 *  Loaded AFTER theme.js so setLanguage / getStoredLanguage are available.
 */

const TRANSLATIONS = {
  // Common / Navigation
  'nav_login':           { en: 'Login',            es: 'Iniciar sesión',          hi: 'लॉगिन' },
  'nav_register':        { en: 'Register',         es: 'Registrarse',             hi: 'पंजीकरण' },
  'nav_dashboard':       { en: 'Dashboard',        es: 'Panel',                   hi: 'डैशबोर्ड' },
  'nav_predict':         { en: 'Predict',          es: 'Predecir',                hi: 'भविष्यवाणी' },
  'nav_history':         { en: 'History',          es: 'Historial',               hi: 'इतिहास' },
  'nav_profile':         { en: 'Profile',          es: 'Perfil',                  hi: 'प्रोफ़ाइल' },
  'nav_admin':           { en: '🛡️ Admin',         es: '🛡️ Admin',                 hi: '🛡️ एडमिन' },
  'nav_logout':          { en: 'Logout',           es: 'Cerrar sesión',           hi: 'लॉग आउट' },
  'back_btn':            { en: '← Back',           es: '← Atrás',                 hi: '← वापस' },
  'dashboard_link':      { en: 'Dashboard →',      es: 'Panel →',                 hi: 'डैशबोर्ड →' },
  'new_prediction_arrow':{ en: 'New Prediction →',  es: 'Nueva predicción →',      hi: 'नई भविष्यवाणी →' },

  // Index page
  'index_title':         { en: 'VegCheck AI - Vegetable Quality Detection', es: 'VegCheck AI - Detección de Calidad de Verduras', hi: 'वीगचेक एआई - सब्ज़ी गुणवत्व पहचान' },
  'index_hero_badge':    { en: '✨ AI-Powered Quality Detection', es: '✨ Detección de Calidad con IA', hi: '✨ एआई-सशक्त गुणवत्व पहचान' },
  'index_hero_title':    { en: 'Detect Vegetable Quality Instantly', es: 'Detecta la calidad de los vegetales al instante', hi: 'तुरंत सब्ज़ी की गुणवत्व पहचानें' },
  'index_hero_sub':      { en: 'Upload an image and get instant AI analysis — fresh, moderate, or rotten — with confidence scores and downloadable PDF reports.', es: 'Carga una imagen y obtén análisis de IA instantáneo — fresco, moderado o podrido — con puntuaciones de confianza e informes PDF descargables.', hi: 'एक छवि अपलोड करें और तुरंत एआई विश्लेषण प्राप्त करें — ताज़ा, मध्यम या सड़ा — विश्वास स्कोर और डाउनलोड योग्य पीडीएफ़ रिपोर्ट के साथ।' },
  'index_login_btn':     { en: '🔑 Login',         es: '🔑 Iniciar sesión',        hi: '🔑 लॉगिन' },
  'index_register_btn':  { en: 'Create Free Account', es: 'Crear cuenta gratuita', hi: 'नि:शुल्क खाता बनाएं' },
  'index_no_credit':     { en: '✅ No credit card', es: '✅ Sin tarjeta de crédito', hi: '✅ कोई क्रेडिट कार्ड नहीं' },
  'index_instant':       { en: '✅ Instant results', es: '✅ Resultados instantáneos', hi: '✅ तुरंत परिणाम' },
  'index_pdf_export':    { en: '✅ Free PDF export', es: '✅ Exportación PDF gratis', hi: '✅ मुफ्त PDF एक्सपोर्ट' },
  'index_features_title':{ en: 'Everything You Need', es: 'Todo lo que necesitas', hi: 'ज़रूरत सब कुछ' },
  'index_features_sub':  { en: 'Powerful features built for accuracy and ease of use', es: 'Características potentes diseñadas para precisión y facilidad de uso', hi: 'सटीकता और उपयोग की सुविधा के लिए निर्मित शक्तिशाली फीचर' },
  'feature_ai_title':    { en: 'Smart AI Analysis', es: 'Análisis de IA inteligente', hi: 'स्मार्ट एआई विश्लेषण' },
  'feature_ai_desc':     { en: 'MobileNetV2 transfer learning classifies vegetable quality from any image with high accuracy.', es: 'El aprendizaje por transferencia MobileNetV2 clasifica la calidad de las verduras desde cualquier imagen con alta precisión.', hi: 'MobileNetV2 ट्रांसफर लर्निंग कोई भी छवि से सब्ज़ी की गुणवत्व को उच्च सटीकता के साथ वर्गीकृत करता है।' },
  'feature_pdf_title':   { en: 'Instant PDF Reports', es: 'Informes PDF instantáneos', hi: 'तुरंत PDF रिपोर्ट' },
  'feature_pdf_desc':    { en: 'Download professional reports with quality label, confidence score, and actionable recommendations.', es: 'Descarga informes profesionales con etiqueta de calidad, puntuación de confianza y recomendaciones accionables.', hi: 'गुणवत्व लेबल, विश्वास स्कोर और कार्रवाई योग्य सिफ़ारिशों के साथ पेशेवर रिपोर्ट डाउनलोड करें।' },
  'feature_secure_title':{ en: 'Secure & Private', es: 'Seguro y privado', hi: 'सुरक्षित और निजी' },
    'feature_secure_desc': { en: 'JWT authentication with protected dashboards, prediction history, and profile management.', es: 'Autenticación JWT con paneles de control protegidos, historial de predicciones y gestión de perfil.', hi: 'सुरक्षित डैशबोर्ड, भविष्यवाणी इतिहास और प्रोफ़ाइल प्रबंधन के साथ JWT प्रमाणीकरण।' },

  // Login page
  'login_title':         { en: 'Login - VegCheck AI', es: 'Iniciar sesión - VegCheck AI', hi: 'लॉगिन - वीगचेक एआई' },
  'login_welcome':       { en: 'Welcome Back', es: 'Bienvenido de nuevo', hi: 'वापसी स्वागत है' },
  'login_sub':           { en: 'Sign in to access your dashboard, predictions, and quality reports.', es: 'Inicia sesión para acceder a tu panel, predicciones e informes de calidad.', hi: 'अपने डैशबोर्ड, भविष्यवाणियों और गुणवत्व रिपोर्टों तक पहुँचने के लिए साइन इन करें।' },
  'login_signin':        { en: 'Sign In', es: 'Iniciar sesión', hi: 'साइन इन करें' },
  'login_credentials':   { en: 'Enter your credentials to continue', es: 'Introduce tus credenciales para continuar', hi: 'जारी रखने के लिए अपना क्रेडेंशियल दर्ज़ करें' },
  'login_email_label':   { en: 'Email Address', es: 'Dirección de correo', hi: 'ईमेल पता' },
  'login_email_placeholder': { en: 'you@example.com', es: 'tu@ejemplo.com', hi: 'आपका@उदाहरण.com' },
  'login_password_label':{ en: 'Password', es: 'Contraseña', hi: 'पासवर्ड' },
  'login_password_placeholder': { en: 'Your password', es: 'Tu contraseña', hi: 'आपका पासवर्ड' },
    'login_no_account':    { en: "Don't have an account?", es: '¿No tienes cuenta?', hi: 'खाता नहीं है?' },
  'create_account_link':  { en: 'Create one', es: 'Crear una', hi: 'एक बनाएं' },
  'analytics_dashboard': { en: 'Analytics Dashboard', es: 'Panel de analíticas', hi: 'एनालिटिक्स डैशबोर्ड' },
  'prediction_history':  { en: 'Prediction History', es: 'Historial de predicciones', hi: 'भविष्यवाणी इतिहास' },
  'pdf_report_export':   { en: 'PDF Report Export', es: 'Exportación de informes PDF', hi: 'पीडीएफ़ रिपोर्ट निर्यात' },
  'profile_management':  { en: 'Profile Management', es: 'Gestión de perfil', hi: 'प्रोफ़ाइल प्रबंधन' },
  'signing_in':          { en: 'Signing in...', es: 'Iniciando sesión...', hi: 'साइन इन कर रहा है...' },

  // Register page
  'register_title':      { en: 'Register - VegCheck AI', es: 'Registrarse - VegCheck AI', hi: 'पंजीकरण - वीगचेक एआई' },
  'register_welcome':    { en: 'Join VegCheck AI', es: 'Únete a VegCheck AI', hi: 'वीगचेक एआई से जुड़ें' },
  'register_sub':        { en: 'AI-powered vegetable quality detection with instant confidence scores and PDF reports.', es: 'Detección de calidad de verduras con IA con puntuaciones de confianza instantáneas e informes PDF.', hi: 'तत्काल विश्वास स्कोर और पीडीएफ़ रिपोर्ट के साथ एआई-सशक्त सब्ज़ी गुणवत्व पहचान।' },
  'register_full_name':  { en: 'Full Name', es: 'Nombre completo', hi: 'पूरा नाम' },
  'register_full_name_placeholder': { en: 'John Doe', es: 'John Doe', hi: 'जॉन डो' },
  'register_username':   { en: 'Username', es: 'Nombre de usuario', hi: 'उपयोगकर्ता नाम' },
  'register_username_placeholder': { en: 'john_doe', es: 'john_doe', hi: 'john_doe' },
  'register_email_label': { en: 'Email Address', es: 'Dirección de correo', hi: 'ईमेल पता' },
  'register_email_placeholder': { en: 'you@example.com', es: 'tu@ejemplo.com', hi: 'आपका@उदाहरण.com' },
  'register_phone':      { en: 'Phone Number', es: 'Número de teléfono', hi: 'फ़ोन नंबर' },
  'register_phone_placeholder': { en: '+1 234 567 8900', es: '+1 234 567 8900', hi: '+1 234 567 8900' },
  'register_password':   { en: 'Password', es: 'Contraseña', hi: 'पासवर्ड' },
  'register_password_placeholder': { en: 'Your password', es: 'Tu contraseña', hi: 'आपका पासवर्ड' },
  'register_confirm':    { en: 'Confirm Password', es: 'Confirmar contraseña', hi: 'पासवर्ड पुष्टि करें' },
  'register_confirm_placeholder': { en: 'Repeat password', es: 'Repite la contraseña', hi: 'पासवर्ड दोहराएं' },
  'register_terms_text': { en: 'I agree to the', es: 'Acepto los', hi: 'मैं सहमत हूँ' },
  'register_terms_label': { en: 'Terms of Service', es: 'Términos de servicio', hi: 'सेवा की शर्तें' },
  'register_terms_and':  { en: ' & ', es: ' y ', hi: ' और ' },
  'register_privacy_label': { en: 'Privacy Policy', es: 'Política de privacidad', hi: 'निजीता नीति' },
  'register_btn':        { en: 'Create Account', es: 'Crear cuenta', hi: 'खाता बनाएं' },
  'creating_account':    { en: 'Creating account...', es: 'Creando cuenta...', hi: 'खाता बना रहा है...' },
  'register_have_account':{ en: 'Already have an account?', es: '¿Ya tienes cuenta?', hi: 'पास पहले से खाता है?' },
    'register_sign_in':    { en: 'Sign in', es: 'Iniciar sesión', hi: 'साइन इन करें' },
  'register_subtitle':   { en: 'Fill in your details to get started', es: 'Rellena tus datos para comenzar', hi: 'शुरू करने के लिए अपने विवरण भरें' },
  'feature_model':       { en: 'MobileNetV2 AI Model', es: 'Modelo de IA MobileNetV2', hi: 'MobileNetV2 एआई मॉडल' },
  'feature_confidence':  { en: 'Confidence Score Analysis', es: 'Análisis de puntuación de confianza', hi: 'विश्वास स्कोर विश्लेषण' },
  'feature_downloads':   { en: 'Downloadable PDF Reports', es: 'Informes PDF descargables', hi: 'डाउनलोड योग्य PDF रिपोर्ट' },
    'feature_jwt':         { en: 'JWT Secured Access', es: 'Acceso protegido con JWT', hi: 'JWT सुरक्षित पहुँच' },
  'register_success':    { en: 'Account created! Redirecting to login...', es: '¡Cuenta creada! Redirigiendo al inicio de sesión...', hi: 'खाता बनाया गया! लॉगिन पर रीडायरेक्ट कर रहा है...' },
  'register_full_placeholder': { en: 'John Doe', es: 'John Doe', hi: 'जॉन डो' },
  'register_user_placeholder': { en: 'john_doe', es: 'john_doe', hi: 'john_doe' },
  'register_email_placeholder': { en: 'you@example.com', es: 'tu@example.com', hi: 'आप@example.com' },
  'register_phone_placeholder': { en: '+1 234 567 8900', es: '+1 234 567 8900', hi: '+1 234 567 8900' },
  'register_pw_placeholder':  { en: 'Min. 6 chars', es: 'Mín. 6 caracteres', hi: 'न्यूनतम 6 अक्षर' },
  'register_confirm_placeholder': { en: 'Repeat password', es: 'Repetir contraseña', hi: 'पासवर्ड दोहराएं' },
  'password_min':        { en: 'Password must be at least 6 characters.', es: 'La contraseña debe tener al menos 6 caracteres.', hi: 'पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।' },
  'passwords_mismatch':  { en: 'Passwords do not match.', es: 'Las contraseñas no coinciden.', hi: 'पासवर्ड मेल नहीं खाते।' },
  'terms_required':      { en: 'Please accept the Terms of Service to continue.', es: 'Por favor, acepta los Términos de servicio para continuar.', hi: 'जारी रखने के लिए कृपया सेवा की शर्तें स्वीकार करें।' },
  'register_failed':     { en: 'Registration failed. Please try again.', es: 'El registro falló. Por favor, inténtalo de nuevo.', hi: 'पंजीकरण विफल। कृपया पुनः प्रयास करें।' },
    'cannot_connect':      { en: 'Cannot connect to server. Make sure the backend is running.', es: 'No se puede conectar al servidor. Asegúrate de que el backend esté en ejecución.', hi: 'सर्वर से कनेक्ट नहीं हो सकता। सुनिश्चित करें कि बैकएंड चल रहा है।' },

  // Dashboard page
  'dashboard_title':     { en: 'Dashboard - VegCheck AI', es: 'Panel - VegCheck AI', hi: 'डैशबोर्ड - वीगचेक एआई' },
  'dashboard_heading':   { en: 'Dashboard', es: 'Panel', hi: 'डैशबोर्ड' },
  'dashboard_sub':       { en: 'Your quality detection overview', es: 'Resumen de detección de calidad', hi: 'आपका गुणवत्व पहचान अवलोकन' },
  'stat_total':          { en: 'Total', es: 'Total', hi: 'कुल' },
  'stat_fresh':          { en: 'Fresh', es: 'Fresco', hi: 'ताज़ा' },
  'stat_moderate':       { en: 'Moderate', es: 'Moderado', hi: 'मध्यम' },
  'stat_rotten':         { en: 'Rotten', es: 'Podrido', hi: 'सड़ा' },
  'recent_predictions':  { en: '🕒 Recent Predictions', es: '🕒 Predicciones recientes', hi: '🕒 हालिया भविष्यवाणियाँ' },
  'quick_actions':       { en: '⚡ Quick Actions', es: '⚡ Acciones rápidas', hi: '⚡ त्वरित क्रियाएँ' },
  'new_prediction':      { en: '🔍 New Prediction', es: '🔍 Nueva predicción', hi: '🔍 नई भविष्यवाणी' },
  'my_profile':          { en: '👤 My Profile', es: '👤 Mi perfil', hi: '👤 मेरी प्रोफ़ाइल' },
  'no_predictions':      { en: 'No predictions yet.', es: 'Aún no hay predicciones.', hi: 'अभी तक कोई भविष्यवाणी नहीं है।' },
  'make_first':          { en: 'Make your first one!', es: '¡Haz la primera!', hi: 'पहली भविष्यवाणी करें!' },
  'failed_load_dashboard': { en: 'Failed to load dashboard', es: 'Error al cargar el panel', hi: 'डैशबोर्ड लोड करने में विफल' },

  // Predict page
  'predict_title':       { en: 'Predict - VegCheck AI', es: 'Predecir - VegCheck AI', hi: 'भविष्यवाणी - वीगचेक एआई' },
  'upload_image':        { en: '📤 Upload Image', es: '📤 Subir imagen', hi: '📤 छवि अपलोड करें' },
  'upload_zone_text':    { en: 'Click to choose or drag & drop', es: 'Haz clic para elegir o arrastra y suelta', hi: 'चुनने या ड्रैग एंड ड्रॉप करने के लिए क्लिक करें' },
  'upload_zone_sub':     { en: 'JPG, PNG, WEBP supported', es: 'JPG, PNG, WEBP compatibles', hi: 'JPG, PNG, WEBP समर्थित' },
  'analyse_quality':     { en: '🔍 Analyse Quality', es: '🔍 Analizar calidad', hi: '🔍 गुणवत्व विश्लेषण' },
  'batch_analyse':       { en: '📦 Batch Analyse', es: '📦 Análisis por lotes', hi: '📦 बैच विश्लेषण' },
  'prediction_result':   { en: 'Prediction Result', es: 'Resultado de la predicción', hi: 'भविष्यवाणी परिणाम' },
  'analysis_placeholder': { en: 'Your analysis will appear here after uploading an image.', es: 'Tu análisis aparecerá aquí después de cargar una imagen.', hi: 'छवि अपलोड करने के बाद आपका विश्लेषण यहाँ दिखेगा।' },
  'confidence':          { en: 'Confidence', es: 'Confianza', hi: 'विश्वास' },
  'recommendation':      { en: 'Recommendation', es: 'Recomendación', hi: 'सिफ़ारिश' },
  'storage_life':        { en: 'Storage Life', es: 'Vida de almacenamiento', hi: 'भंडारण जीवन' },
  'storage_temperature': { en: 'Storage Temperature', es: 'Temperatura de almacenamiento', hi: 'भंडारण तापमान' },
  'download_pdf':        { en: '📄 Download PDF', es: '📄 Descargar PDF', hi: '📄 PDF डाउनलोड' },
  'view_history_short':  { en: 'View History', es: 'Ver historial', hi: 'इतिहास देखें' },
  'analysing_image':     { en: 'Analysing image...', es: 'Analizando imagen...', hi: 'छवि विश्लेषण...' },
  'analysing_images':    { en: 'Analysing images...', es: 'Analizando imágenes...', hi: 'छवियों का विश्लेषण...' },
  'click_for_detail':    { en: 'Click for detailed analysis', es: 'Haz clic para análisis detallado', hi: 'विस्तृत विश्लेषण के लिए क्लिक करें' },
  'no_thumbnail':        { en: 'no thumbnail', es: 'sin miniatura', hi: 'थंबनेल नहीं' },
  'download_all_batch':  { en: '📥 Download All Batch Analysis', es: '📥 Descargar todo el análisis por lotes', hi: '📥 सभी बैच विश्लेषण डाउनलोड करें' },
  'batch_result':        { en: 'Batch Result', es: 'Resultado por lotes', hi: 'बैच परिणाम' },
  'batch_results':       { en: 'Batch Prediction Results', es: 'Resultados de predicción por lotes', hi: 'बैच भविष्यवाणी परिणाम' },
  'images_count':        { en: 'images - click any thumbnail for full detail', es: 'imágenes - haz clic en cualquier miniatura para detalles completos', hi: 'छवियाँ - पूरा विवरण पाने के लिए किसी भी थंबनेल पर क्लिक करें' },
  'no_valid_images':     { en: 'No valid images were processed.', es: 'No se procesaron imágenes válidas.', hi: 'कोई वैध छवि संसाधित नहीं हुई।' },
  'change_photo':        { en: '↺ Change photo', es: '↺ Cambiar foto', hi: '↺ फ़ोटो बदलें' },
  'change_selection':    { en: '↺ Change selection', es: '↺ Cambiar selección', hi: '↺ चयन बदलें' },
  'multiple_images':     { en: 'Multiple images selected.', es: 'Múltiples imágenes seleccionadas.', hi: 'कई छवियाँ चयनित।' },
  'choose_image':        { en: 'Please choose an image first.', es: 'Por favor, elige una imagen primero.', hi: 'कृपया पहले एक छवि चुनें।' },
    'select_2_images':     { en: 'Select 2 or more images to batch-analyse.', es: 'Selecciona 2 o más imágenes para analizar por lotes.', hi: 'बैच विश्लेषण के लिए 2 या अधिक छवि चुनें।' },

  // History page
  'history_title':       { en: 'History - VegCheck AI', es: 'Historial - VegCheck AI', hi: 'इतिहास - वीगचेक एआई' },
  'history_heading':     { en: 'Prediction History', es: 'Historial de predicciones', hi: 'भविष्यवाणी इतिहास' },
  'history_sub':         { en: 'All your past analyses', es: 'Todos tus análisis anteriores', hi: 'आपके सभी पिछले विश्लेषण' },
  'pdf_btn':             { en: '📄 PDF', es: '📄 PDF', hi: '📄 PDF' },
  'delete_btn':          { en: '🗑 Delete', es: '🗑 Eliminar', hi: '🗑 हटाएं' },
  'cannot_connect_server': { en: 'Cannot connect to server.', es: 'No se puede conectar al servidor.', hi: 'सर्वर से कनेक्ट नहीं हो सकता।' },
  'new_prediction_arrow_short': { en: 'New Prediction →', es: 'Nueva predicción →', hi: 'नई भविष्यवाणी →' },

  // Profile page
  'profile_title':       { en: 'Profile - VegCheck AI', es: 'Perfil - VegCheck AI', hi: 'प्रोफ़ाइल - वीगचेक एआई' },
  'profile_heading':     { en: 'My Profile', es: 'Mi perfil', hi: 'मेरी प्रोफ़ाइल' },
  'edit_profile':        { en: 'Edit Profile', es: 'Editar perfil', hi: 'प्रोफ़ाइल एडिट करें' },
  'save_changes':        { en: 'Save Changes', es: 'Guardar cambios', hi: 'बदलाव सहेजें' },
  'cancel':              { en: 'Cancel', es: 'Cancelar', hi: 'रद्द करें' },
  'username':            { en: 'Username', es: 'Usuario', hi: 'उपयोगकर्ता नाम' },
  'email':               { en: 'Email', es: 'Correo', hi: 'ईमेल' },
  'full_name':           { en: 'Full Name', es: 'Nombre Completo', hi: 'पूरा नाम' },
  'phone':               { en: 'Phone', es: 'Teléfono', hi: 'फ़ोन' },
  'phone_number':        { en: 'Phone Number', es: 'Número de teléfono', hi: 'फ़ोन नंबर' },
  'profile_picture':     { en: 'Profile Picture', es: 'Foto de perfil', hi: 'प्रोफ़ाइल चित्र' },
  'no_image_selected':   { en: 'No image selected', es: 'No se seleccionó imagen', hi: 'कोई छवि नहीं चुनी गई' },
  'invalid_phone':       { en: 'Please enter a valid phone number.', es: 'Por favor, introduce un número de teléfono válido.', hi: 'कृपया एक वैध फ़ोन नंबर दर्ज़ करें।' },
  'failed_save_profile': { en: 'Failed to save profile.', es: 'Error al guardar el perfil.', hi: 'प्रोफ़ाइल सहेजने में विफल।' },
    'profile_cannot_connect': { en: 'Cannot connect to server.', es: 'No se puede conectar al servidor.', hi: 'सर्वर से कनेक्ट नहीं हो सकता।' },

  // Admin page
  'admin_title':         { en: 'Admin - VegCheck AI', es: 'Admin - VegCheck AI', hi: 'एडमिन - वीगचेक एआई' },
  'train_model':         { en: '🤖 Train Model', es: '🤖 Entrenar modelo', hi: '🤖 मॉडल प्रशिक्षण' },
  'train_desc':          { en: 'Upload a ZIP of labelled vegetable images to retrain the AI model.', es: 'Carga un ZIP de imágenes de verduras etiquetadas para reentrenar el modelo de IA.', hi: 'AI मॉडल को फिर से प्रशिक्षित करने के लिए लेबल्ड सब्ज़ी की छवियों का ZIP अपलोड करें।' },
  'required_zip':        { en: 'Required ZIP structure:', es: 'Estructura ZIP requerida:', hi: 'आवश्यक ZIP संरचना:' },
  'quality_folders':     { en: 'Quality folder names recognised:', es: 'Nombres de carpetas de calidad reconocidos:', hi: 'पहचाने गए गुणवत्व फ़ोल्डर नाम:' },
  'fresh_label':         { en: 'Fresh', es: 'Fresco', hi: 'ताज़ा' },
  'moderate_label':      { en: 'Moderately Fresh', es: 'Moderadamente fresco', hi: 'मध्यम ताज़ा' },
  'rotten_label':        { en: 'Rotten', es: 'Podrido', hi: 'सड़ा' },
  'single_image_mode':   { en: 'Single-image mode:', es: 'Modo de imagen única:', hi: 'सिंगल इमेज मोड:' },
  'single_image_instructions': { en: 'Upload one photo at a time, choose the vegetable and quality, and the image will be added to the training dataset.', es: 'Sube una foto a la vez, elige la verdura y la calidad, y la imagen se añadirá al conjunto de datos de entrenamiento.', hi: 'एक बार में एक फोटो अपलोड करें, सब्ज़ी और गुणवत्व चुनें, और छवि प्रशिक्षण डेटासेट में जोड़ी जाएगी।' },
  'upload_zip':          { en: 'Click or drag & drop your ZIP file here', es: 'Haz clic o arrastra y suelta tu archivo ZIP aquí', hi: 'यहाँ अपना ZIP फ़ाइल क्लिक या ड्रैग एंड ड्रॉप करें' },
  'zip_only':            { en: 'Only .zip files accepted', es: 'Solo se aceptan archivos .zip', hi: 'केवल .zip फ़ाइलें स्वीकृत' },
  'epochs_label':        { en: 'Epochs:', es: 'Épocas:', hi: 'एपोक्स:' },
  'start_training':      { en: '🚀 Start Training', es: '🚀 Iniciar entrenamiento', hi: '🚀 प्रशिक्षण शुरू करें' },
  'uploading':           { en: 'Uploading...', es: 'Subiendo...', hi: 'अपलोड कर रहा है...' },
  'training':            { en: '⏳ Training...', es: '⏳ Entrenando...', hi: '⏳ प्रशिक्षण...' },
  'train_from_folder':   { en: '📁 Train from Existing Folder', es: '📁 Entrenar desde carpeta existente', hi: '📁 मौजूदा फ़ोल्डर से प्रशिक्षण' },
  'train_from_folder_desc': { en: 'Train directly from the train_uploads folder already on the server.', es: 'Entrena directamente desde la carpeta train_uploads ya en el servidor.', hi: 'सर्वर पर मौजूदा train_uploads फ़ोल्डर से सीधे प्रशिक्षण प्राप्त करें।' },
  'vegetable_name':      { en: 'Vegetable', es: 'Verdura', hi: 'सब्ज़ी' },
  'vegetable_name_label':{ en: 'Vegetable name', es: 'Nombre de la verdura', hi: 'सब्ज़ी का नाम' },
  'quality_label':       { en: 'Quality', es: 'Calidad', hi: 'गुणवत्व' },
  'vegetable_placeholder': { en: 'Tomato', es: 'Tomate', hi: 'टमाटर' },
  'single_image':        { en: 'Single image', es: 'Imagen individual', hi: 'सिंगल इमेज' },
  'add_single':          { en: '📸 Add Single Image', es: '📸 Añadir imagen individual', hi: '📸 सिंगल इमेज जोड़ें' },
  'adding':              { en: 'Adding...', es: 'Añadiendo...', hi: 'जोड़ रहा है...' },
  'training_log':        { en: 'Training Log', es: 'Registro de entrenamiento', hi: 'प्रशिक्षण लॉग' },
  'clear_log':           { en: 'Clear', es: 'Borrar', hi: 'साफ़ करें' },
  'waiting_training':    { en: 'Waiting for training to start...', es: 'Esperando a que comience el entrenamiento...', hi: 'प्रशिक्षण शुरू होने की प्रतीक्षा...' },
  'all_users':           { en: '👥 All Users', es: '👥 Todos los usuarios', hi: '👥 सभी उपयोगकर्ता' },
  'user_role_admin':     { en: 'Admin', es: 'Admin', hi: 'एडमिन' },
  'user_role_user':      { en: 'User', es: 'Usuario', hi: 'उपयोगकर्ता' },
  'access_denied':       { en: 'Access denied.', es: 'Acceso denegado.', hi: 'एक्सेस अस्वीकृत।' },
  'no_users':            { en: 'No users found.', es: 'No se encontraron usuarios.', hi: 'कोई उपयोगकर्ता नहीं मिला।' },
  'select_zip_first':    { en: 'Please select a ZIP file first.', es: 'Por favor, selecciona un archivo ZIP primero.', hi: 'कृपया पहले एक ZIP फ़ाइल चुनें।' },
  'select_image_first':  { en: 'Please select a single image first.', es: 'Por favor, selecciona una imagen individual primero.', hi: 'कृपया पहले एक सिंगल इमेज चुनें।' },
  'enter_vegetable':     { en: 'Please enter a vegetable name.', es: 'Por favor, introduce el nombre de una verdura.', hi: 'कृपया एक सब्ज़ी का नाम दर्ज़ करें।' },
  'training_started':    { en: 'Training started!', es: '¡Entrenamiento iniciado!', hi: 'प्रशिक्षण शुरू हो गया!' },
  'classes_csv':         { en: 'Classes:', es: 'Clases:', hi: 'क्लासेज़:' },
  'upload_failed':       { en: 'Upload failed.', es: 'Error al subir.', hi: 'अपलोड विफल।' },
  'training_failed':     { en: 'Training failed to start.', es: 'Error al iniciar el entrenamiento.', hi: 'प्रशिक्षण शुरू करने में विफल।' },
  'single_upload_failed': { en: 'Single-image upload failed.', es: 'Error al subir la imagen individual.', hi: 'सिंगल इमेज अपलोड विफल।' },
  'image_added':         { en: 'Image added. Training started!', es: '¡Imagen añadida. Entrenamiento iniciado!', hi: 'छवि जोड़ी गई। प्रशिक्षण शुरू हो गया!' },
  'stream_error':        { en: 'Log stream error: ', es: 'Error de flujo de registro: ', hi: 'लॉग स्ट्रीम त्रुटि: ' },
  'drop_zip':            { en: 'Please drop a .zip file.', es: 'Arrastra un archivo .zip.', hi: 'कृपया .zip फ़ाइल ड्रॉप करें।' },
  'select_file':         { en: 'Please select a file first.', es: 'Por favor, selecciona un archivo primero.', hi: 'कृपया पहले एक फ़ाइल चुनें।' },

  // Chatbot
  'chatbot_title':       { en: 'VegCheck AI Assistant', es: 'Asistente VegCheck AI', hi: 'वीगचेक एआई सहायक' },
  'chatbot_placeholder': { en: 'Ask a question...', es: 'Pregunta algo...', hi: 'कोई प्रश्न पूछें...' },
  'chatbot_send':        { en: 'Send', es: 'Enviar', hi: 'भेजें' },
  'chatbot_welcome':     { en: "Hello! I'm the VegCheck AI assistant. How can I help you today?", es: '¡Hola! Soy el asistente de VegCheck AI. ¿En qué puedo ayudarte hoy?', hi: 'नमस्ते! मैं वीगचेक एआई सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?' },
  'chatbot_typing':      { en: 'Typing...', es: 'Escribiendo...', hi: 'लिखा रहा है...' },
  'chatbot_no_match':    { en: "I'm not sure about that. Try asking about: how to use, how to predict, how to login, or the user guide.", es: 'No estoy seguro de eso. Intenta preguntar sobre: cómo usar, cómo predecir, cómo iniciar sesión o guía de usuario.', hi: 'मुझे इसके बारे में नहीं पता। कोशिश करें: कैसे उपयोग करें, कैसे भविष्यवाणी करें, कैसे लॉगिन करें, या यूज़र गाइड।' },

  // Chatbot FAQ answers (multi-line)
  'faq_how_to_use':      { en: 'VegCheck AI lets you detect vegetable quality in seconds. 1) Register — Create a free account. 2) Login — Sign in with your email and password. 3) Upload — Go to Predict and upload a vegetable image (JPG/PNG/WEBP). 4) Analyse — Click Analyse Quality for an instant prediction (Fresh, Moderately Fresh, or Rotten) with confidence score. 5) Report — Download a PDF report with recommendations. 6) History — View all past predictions.', es: 'VegCheck AI te permite detectar la calidad de las verduras en segundos. 1) Regístrate. 2) Inicia sesión. 3) Sube — Ve a Predecir y sube una imagen (JPG/PNG/WEBP). 4) Analiza — Haz clic en Analizar calidad para una predicción instantánea. 5) Informe — Descarga un PDF con recomendaciones. 6) Historial — Consulta todas las predicciones.', hi: 'वीगचेक एआई आपको सेकंड में सब्ज़ी की गुणवत्व पहचान सकता है। 1) पंजीकरण। 2) लॉगिन। 3) अपलोड — प्रेडिक्ट पर जाएँ। 4) विश्लेषण — Analyse Quality पर क्लिक। 5) रिपोर्ट — PDF डाउनलोड। 6) इतिहास — सभी पिछली भविष्यवाणियों को देखें।' },
  'faq_how_to_predict':  { en: 'To predict: 1) Login. 2) Go to Predict page. 3) Upload an image (JPG/PNG/WEBP). 4) Click Analyse Quality for single, or Batch Analyse for 2+ images. 5) MobileNetV2 classifies as Fresh, Moderately Fresh, or Rotten with % confidence. 6) View heatmap. 7) Download PDF or View History.', es: 'Para predecir: 1) Inicia sesión. 2) Ve a Predecir. 3) Sube una imagen (JPG/PNG/WEBP). 4) Analizar calidad (individual) o Análisis por lotes (2+). 5) MobileNetV2 clasifica como Fresco, Moderadamente fresco o Podrido. 6) Ver mapa de calor. 7) Descargar PDF o Ver historial.', hi: 'भविष्यवाणी करने के लिए: 1) लॉगिन। 2) Predict पेज पर जाएँ। 3) JPG/PNG/WEBP छवि अपलोड करें। 4) Analyse Quality (सिंगल) या Batch Analyse (2+) पर क्लिक। 5) MobileNetV2 Fresh, Moderately Fresh या Rotten के रूप में %। 6) हीटमैप देखें। 7) PDF डाउनलोड या View History।' },
    'faq_how_to_login':    { en: 'To log in: 1) Click Login in the top nav bar. 2) Enter your Email Address and Password. 3) Click Sign In. 4) Redirected to Dashboard. Tip: If no account, click Create Free Account first.', es: 'Para iniciar sesión: 1) Haz clic en Iniciar sesión. 2) Introduce tu Email y Contraseña. 3) Haz clic en Iniciar sesión. 4) Redirigido al Panel. Consejo: Si no tienes cuenta, crea una primero.', hi: 'लॉग इन करने के लिए: 1) ऊपरी नेविगेशन में Login पर क्लिक करें। 2) अपना Email और Password दर्ज़ करें। 3) Sign In पर क्लिक करें। 4) डैशबोर्ड पर रीडायरेक्ट। टिप: अगर खाता नहीं है, तो पहले Create Free Account क्लिक करें।' },
  'faq_user_guide':      { en: 'User Guide: Account - Register free, login, update profile. Predicting - Upload on Predict page, Analyse Quality or Batch Analyse. Results show quality label, confidence %, storage life, recommendations. Reports - Download PDF or batch ZIP. History - View, download, delete predictions. Admin - Train model, upload datasets, manage users. Tips - JPG/PNG/WEBP. Dark/Light mode and EN/ES/HI in top bar.', es: 'Guía: Cuenta - Regístrate gratis, inicia sesión. Predecir - Sube en Predecir, Analizar calidad o Análisis por lotes. Resultados: etiqueta, % confianza, vida de almacenamiento, recomendaciones. Informes - PDF o ZIP. Historial - Ver, descargar, eliminar. Admin - Entrena modelo, sube datasets. Consejos - JPG/PNG/WEBP. Modo oscuro/claro y EN/ES/HI.', hi: 'यूज़र गाइड: खाता - नि:शुल्क पंजीकरण, लॉगिन, प्रोफ़ाइल अपडेट। भविष्यवाणी - Predict पर अपलोड, Analyse Quality या Batch Analyse। परिणाम: लेबल, % विश्वास, भंडारण जीवन, सिफ़ारिशें। रिपोर्ट्स - PDF या ZIP। इतिहास - देखें, डाउनलोड, हटाएं। Admin - मॉडल प्रशिक्षण, डेटासेट अपलोड। टिप्स - JPG/PNG/WEBP। डार्क/लाइट मोड और EN/ES/HI।' },
  'faq_how_to_register': { en: 'To create an account: 1) Click Create Free Account. 2) Fill in Full Name, Username, Email, Phone, Password (min 6 chars), Confirm Password. 3) Agree to Terms. 4) Click Create Account. 5) Redirected to login. Tip: Use a valid email.', es: 'Para crear una cuenta: 1) Crear cuenta gratuita. 2) Nombre, Usuario, Email, Teléfono, Contraseña (mín 6), Confirmar. 3) Acepta Términos. 4) Crear cuenta. 5) Redirigido a login. Consejo: Usa un email válido.', hi: 'खाता बनाने के लिए: 1) Create Free Account पर क्लिक करें। 2) Full Name, Username, Email, Phone, Password (मिन 6 अक्षर), Confirm Password। 3) Terms से सहमत। 4) Create Account पर क्लिक। 5) लॉगिन पर रीडायरेक्ट। टिप: एक वैध email उपयोग करें।' },
  'faq_how_to_download_pdf': { en: 'To download a PDF: 1) After getting a prediction on Predict page, click Download PDF. 2) PDF includes quality label, confidence score, storage life, temp, recommendations. 3) For batch, click Download All Batch Analysis for ZIP with heatmaps. 4) In History, click PDF button. Tip: Must be logged in.', es: 'Para descargar un PDF: 1) Después de predecir, haz clic en Descargar PDF. 2) PDF incluye etiqueta, confianza, vida de almacenamiento, temp, recomendaciones. 3) Para lotes, Descargar todo el análisis. 4) En Historial, haz clic en PDF. Consejo: Debes iniciar sesión.', hi: 'PDF डाउनलोड करने के लिए: 1) Predict पर भविष्यवाणी के बाद, Download PDF पर क्लिक। 2) PDF में लेबल, विश्वास स्कोर, भंडारण जीवन, तापमान, सिफ़ारिशें। 3) बैच के लिए, सभी हीटमैप के साथ ZIP। 4) History में, PDF बटन। टिप: लॉग इन होना आवश्यक है।' },
  'faq_how_to_history':  { en: 'To view history: 1) Login. 2) Click History in nav bar. 3) See predictions with quality, confidence %, storage days, temperature, date. 4) Click PDF to download or Delete to remove. Tip: Access from Dashboard quick actions.', es: 'Para ver historial: 1) Inicia sesión. 2) Haz clic en Historial. 3) Verás predicciones con calidad, %, días, temperatura, fecha. 4) PDF o Delete. Consejo: Desde Panel.', hi: 'इतिहास देखने के लिए: 1) लॉगिन। 2) History पर क्लिक। 3) गुणवत्व, %, दिन, तापमान, तारीख। 4) PDF या Delete पर क्लिक। टिप: डैशबोर्ड से पहुँचें।' },

  // Errors
      'download_failed_msg': { en: 'Unable to download the PDF report right now.', es: 'No se puede descargar el informe PDF en este momento.', hi: 'अभी PDF रिपोर्ट डाउनलोड नहीं किया जा सकता।' },
  'error_generic':       { en: 'Something went wrong.', es: 'Algo salió mal.', hi: 'कुछ गलत हो गया।' },
  'login_success':       { en: 'Login successful! Redirecting...', es: '¡Inicio de sesión exitoso! Redirigiendo...', hi: 'लॉगिन सफल! रीडायरेक्ट कर रहा है...' },
  'fill_all_fields':     { en: 'Please fill in all fields.', es: 'Por favor, completa todos los campos.', hi: 'कृपया सभी फ़ील्ड भरें।' },
  'invalid_credentials': { en: 'Invalid email or password.', es: 'Email o contraseña inválidos.', hi: 'अमान्य ईमेल या पासवर्ड।' },
    'register_failed_msg': { en: 'Registration failed. Please try again.', es: 'El registro falló. Por favor, inténtalo de nuevo.', hi: 'पंजीकरण विफल। कृपया पुनः प्रयास करें।' },
  'register_required_fields': { en: 'Username, email and password are required.', es: 'Se requieren nombre de usuario, email y contraseña.', hi: 'यूज़रनेम, ईमेल और पासवर्ड आवश्यक हैं।' },
  'register_password_min': { en: 'Password must be at least 6 characters.', es: 'La contraseña debe tener al menos 6 caracteres.', hi: 'पासवर्ड कम से कम 6 अक्षर होना चाहिए।' },
  'register_password_mismatch': { en: 'Passwords do not match.', es: 'Las contraseñas no coinciden.', hi: 'पासवर्ड मेल नहीं खाते।' },
  'register_terms_required': { en: 'Please accept the Terms of Service to continue.', es: 'Por favor, acepta los Términos de servicio para continuar.', hi: 'कृपया जारी रखने के लिए सेवा की शर्तों को स्वीकार करें।' },
  'cannot_connect': { en: 'Cannot connect to server. Make sure the backend is running.', es: 'No se puede conectar al servidor. Asegúrate de que el backend esté en ejecución.', hi: 'सर्वर से कनेक्ट नहीं कर सकते। सुनिश्चित करें कि बैकएंड चल रहा है।' },
  'profile_updated':     { en: 'Profile updated successfully.', es: 'Perfil actualizado correctamente.', hi: 'प्रोफ़ाइल सफलतापूर्वक अपडेट हुई।' },
    'no_changes':          { en: 'No changes to save.', es: 'No hay cambios que guardar.', hi: 'सहेजने के लिए कोई बदलाव नहीं।' },

  // Theme toggle & language selector
  'theme_toggle_dark':   { en: '🌙 Dark', es: '🌙 Oscuro', hi: '🌙 डार्क' },
  'theme_toggle_light':  { en: '☀️ Light', es: '☀️ Claro', hi: '☀️ लाइट' },
  'lang_en':             { en: 'English', es: 'Inglés', hi: 'अंग्रेज़ी' },
  'lang_es':             { en: 'Español', es: 'Español', hi: 'स्पेनिश' },
    'lang_hi':             { en: 'हिंदी', es: 'हिंदी', hi: 'हिंदी' },

  // Dashboard page
  'dashboard_title':      { en: 'Dashboard - VegCheck AI', es: 'Panel - VegCheck AI', hi: 'डैशबोर्ड - वीगचेक एआई' },
  'dashboard_heading':    { en: 'Dashboard', es: 'Panel', hi: 'डैशबोर्ड' },
  'dashboard_sub':        { en: 'Your quality detection overview', es: 'Resumen de detección de calidad', hi: 'आपका गुणवत्व पहचान अवलोकन' },
  'dashboard_recent':     { en: 'Recent Predictions', es: 'Predicciones recientes', hi: 'हाल की भविष्यवाणियाँ' },
  'dashboard_quick':      { en: 'Quick Actions', es: 'Acciones rápidas', hi: 'त्वरित कर्रवाई' },
  'dashboard_profile':    { en: 'My Profile', es: 'Mi Perfil', hi: 'मेरा प्रोफ़ाइल' },
  'stats_total':          { en: 'Total', es: 'Total', hi: 'कुल' },
  'stats_fresh':          { en: 'Fresh', es: 'Fresco', hi: 'ताज़ा' },
  'stats_moderate':       { en: 'Moderate', es: 'Moderado', hi: 'मध्यम' },
  'stats_rotten':         { en: 'Rotten', es: 'Puesto', hi: 'सड़ा' },
  'dashboard_no_pred':    { en: 'No predictions yet.', es: 'Aún no hay predicciones.', hi: 'अभी तक कोई भविष्यवाणी नहीं।' },
  'dashboard_make_first': { en: 'Make your first one!', es: '¡Haz la primera!', hi: 'अपनी पहली भविष्यवाणी बनाएं!' },
  'dashboard_load_error': { en: 'Failed to load dashboard', es: 'Error al cargar el panel', hi: 'डैशबोर्ड लोड करने में विफल' },

  // History page
  'history_title':        { en: 'History - VegCheck AI', es: 'Historial - VegCheck AI', hi: 'इतिहास - वीगचेक एआई' },
  'history_heading':      { en: 'Prediction History', es: 'Historial de predicciones', hi: 'भविष्यवाणी इतिहास' },
  'history_sub':          { en: 'All your past analyses', es: 'Todos tus análisis anteriores', hi: 'आपके सभी पिछले विश्लेषण' },
    'history_pdf':          { en: '📄 PDF', es: '📄 PDF', hi: '📄 पीडीएफ' },
  'history_delete':       { en: '🗑 Delete', es: '🗑 Borrar', hi: '🗑 हटाएं' },
  'history_no_pred':      { en: 'No predictions yet.', es: 'Aún no hay predicciones.', hi: 'अभी तक कोई भविष्यवाणी नहीं।' },
  'history_make_first':   { en: 'Make your first one!', es: '¡Haz la primera!', hi: 'अपनी पहली बनाएं!' },
  'history_new_pred':     { en: 'New Prediction →', es: 'Nueva predicción →', hi: 'नई भविष्यवाणी →' },

  // Predict page
  'predict_title':        { en: 'Predict - VegCheck AI', es: 'Predecir - VegCheck AI', hi: 'भविष्यवाणी - वीगचेक एआई' },
  'predict_upload':       { en: '📤 Upload Image', es: '📤 Subir imagen', hi: '📤 छवि अपलोड करें' },
  'predict_click_drag':   { en: 'Click to choose or drag & drop', es: 'Haz clic para elegir o arrastra y suelta', hi: 'चुनने के लिए क्लिक करें या ड्रैग एंड ड्रॉप करें' },
  'predict_supported':    { en: 'JPG, PNG, WEBP supported', es: 'Se admiten JPG, PNG, WEBP', hi: 'JPG, PNG, WEBP समर्थित' },
  'predict_analyse':      { en: '🔍 Analyse Quality', es: '🔍 Analizar calidad', hi: '🔍 गुणवत्व का विश्लेषण' },
  'predict_batch':        { en: '📦 Batch Analyse', es: '📦 Analizar por lotes', hi: '📦 बैच विश्लेषण' },
  'predict_result':       { en: 'Prediction Result', es: 'Resultado de la predicción', hi: 'भविष्यवाणी परिणाम' },
  'predict_no_result':    { en: 'Your analysis will appear here after uploading an image.', es: 'Tu análisis aparecerá aquí después de cargar una imagen.', hi: 'इमेज अपलोड करने के बाद आपका विश्लेषण यहाँ दिखेगा।' },
};

/**
 * Translate a key for the current language.
 * @param {string} key  - translation key
 * @returns {string}    - translated text (falls back to en, then the key itself)
 */
function t(key) {
  const lang = localStorage.getItem('language') || 'en';
  const entry = TRANSLATIONS[key];
  if (entry && entry[lang]) return entry[lang];
  if (entry && entry.en) return entry.en;
  return key;
}

/**
 * Walk every element with a data-key attribute and replace its
 * textContent (or placeholder for inputs) with the localised string.
 */
function translatePage() {
  document.querySelectorAll('[data-key]').forEach(el => {
    const key = el.getAttribute('data-key');
    const txt = t(key);
    if (!txt) return;
    const tag = el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
      if (el.hasAttribute('placeholder')) el.setAttribute('placeholder', txt);
    } else {
      el.textContent = txt;
    }
  });
}

/**
 * Wire up the language <select> that appears on every page.
 * Changing the language re-translates in-place (no reload needed).
 */
function initLanguageSelect() {
  const langSelect = document.getElementById('languageSelect');
  if (!langSelect) return;
  langSelect.value = localStorage.getItem('language') || 'en';
  langSelect.onchange = function () {
    setLanguage(this.value);
    translatePage();
  };
}

// Run once DOM is ready
window.addEventListener('DOMContentLoaded', () => {
  translatePage();
  initLanguageSelect();
});
