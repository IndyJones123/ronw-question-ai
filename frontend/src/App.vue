<script setup lang="ts">
import { computed, ref } from 'vue'

// ---- i18n: EN / ID toggle ----
type Locale = 'id' | 'en'
const locale = ref<Locale>('id')
const t = computed(() => i18n[locale.value])

const i18n = {
  id: {
    // nav
    navFeatures: 'Fitur',
    navHowItWorks: 'Cara Kerja',
    navDownload: 'Download',
    navContact: 'Kontak',
    langLabel: 'EN',
    // hero
    badge: 'Ragnarok New World Quiz Tool',
    heroTitle1: 'Jawaban Quiz',
    heroTitleAccent: 'Instan',
    heroTitle2: 'dari Capture Layar',
    heroDesc: 'Quiz Live OCR menangkap soal di layar kamu, baca pakai OCR, lalu cocokkan ke database soal lokal. Jawaban muncul langsung — tanpa AI, tanpa internet.',
    heroCtaDownload: 'Download Sekarang',
    heroCtaFeatures: 'Lihat Fitur',
    trialLabel: 'Trial Demo',
    // features
    featuresTitle: 'Fitur Utama',
    featuresDesc: 'Semua yang kamu butuh buat jawab quiz cepat dan akurat.',
    features: [
      { icon: 'scan', title: 'Capture Layar Instan', desc: 'Geser box merah ke area soal — aplikasi otomatis screenshot tiap detik tanpa klik.' },
      { icon: 'bolt', title: 'OCR Tanpa Internet', desc: 'Tesseract OCR berjalan lokal di PC kamu. Nggak butuh koneksi, nggak butuh AI.' },
      { icon: 'database', title: 'Database Soal Lokal', desc: 'Soal dicocokkan ke bank data JSON di komputer kamu. Match langsung, jawaban muncul instan.' },
      { icon: 'shield', title: 'Login Aman', desc: 'Backend FastAPI + PostgreSQL. Setiap login tercatat di audit log dengan info device.' },
      { icon: 'rocket', title: 'Dua Mode: OCR & AI', desc: 'Mode Live OCR gratis tanpa AI. Mode AI via CommandCode untuk jawaban lebih akurat.' },
      { icon: 'keyboard', title: 'Hotkey Praktis', desc: 'F9 pause/resume, H hide box, Ctrl+S save log. Full kontrol tanpa lepas keyboard.' },
    ],
    // how it works
    howTitle: 'Cara Kerja',
    howDesc: 'Empat langkah dari buka app sampai jawaban muncul.',
    steps: [
      { num: '01', title: 'Login', desc: 'Buka app, login pakai akun yang sudah dibuat admin.' },
      { num: '02', title: 'Pilih Mode', desc: 'Klik SAGE atau HOPPY untuk pilih database soal.' },
      { num: '03', title: 'Geser Box', desc: 'Arahkan box merah ke soal di layar. OCR jalan otomatis.' },
      { num: '04', title: 'Jawaban Muncul', desc: 'Soal match → jawaban tampil di panel ANSWER instan.' },
    ],
    // pricing / open source & donate
    navPricing: 'Donasi',
    pricingTitle: 'Gratis & Open Source',
    pricingDesc: 'Semua fitur gratis, tanpa biaya, tanpa langganan. Proyek ini open source — kalau suka, boleh donasi.',
    pricingPromoBadge: '100% OPEN SOURCE',
    pricingPromoEnds: 'Tanpa biaya tersembunyi — dari ReogSoloDev',
    pricingBestValue: 'SUKA-SUKA',
    pricingFreeTrial: 'Open Source',
    pricingFreeTrialPrice: 'Rp0',
    pricingFreeTrialPeriod: '/selamanya',
    pricingFreeTrialDesc: 'Semua fitur lengkap gratis selamanya. Tanpa biaya, tanpa trial, tanpa langganan.',
    pricingTrialBtn: 'Download Gratis',
    pricingLifetime: 'Donasi QRIS',
    pricingLifetimeDesc: 'Kalau kamu suka proyek ini, traktir kopi seikhlasnya lewat QRIS. Opsional banget.',
    pricingBuyBtn: 'Donasi via QRIS',
    pricingQrCaption: 'Scan untuk donasi — seikhlasnya',
    pricingDonationName: 'ReogSoloDev · Alfian Dorif Murtadlo',
    pricingIncludesTitle: 'Termasuk:',
    pricingIncludes: [
      'Semua fitur lengkap (OCR + AI mode)',
      'Update database soal',
      'Dukungan via WhatsApp & Discord',
    ],
    // open source project lain
    projectsTitle: 'Open Source Lain dari Kami',
    projectsDesc: 'Proyek open source terkait RonW yang sedang kami kembangkan.',
    projectRmtBadge: 'UNDER DEVELOPMENT',
    projectRmtName: 'RMT-RONW',
    projectRmtDesc: 'Proyek open source terkait RonW yang masih dalam pengembangan.',
    projectRmtRelease: 'Estimasi rilis: 26 Oktober 2026',
    projectRmtSoon: 'Segera Hadir',
    // download
    downloadTitle: 'Download Quiz Live OCR',
    downloadDesc: 'Aplikasi desktop Windows. Download dari Google Drive, ekstrak, jalankan. Login pakai akun dari admin.',
    downloadBtn: 'Download dari Google Drive',
    downloadNoInstall: 'Tanpa install',
    // contact
    contactTitle: 'Hubungi Kami',
    contactDesc: 'Ada pertanyaan? Butuh bantuan setup? Chat kami langsung.',
    waLabel: 'WhatsApp',
    waSub: 'Chat langsung, respon cepat',
    discordLabel: 'Discord',
    discordSub: 'Grup komunitas & support',
    fbLabel: 'Facebook',
    fbSub: 'Halaman & update info',
    // footer
    footerTag: 'Quiz Live OCR — Ragnarok New World',
    footerCopy: '© 2026 REOGSOLODEV. All rights reserved.',
    // placeholder warnings
    envWarningGDrive: '⚠ Link Google Drive belum diisi. Edit',
    envWarningEnv: 'di .env',
  },
  en: {
    // nav
    navFeatures: 'Features',
    navHowItWorks: 'How It Works',
    navDownload: 'Download',
    navContact: 'Contact',
    langLabel: 'ID',
    // hero
    badge: 'Ragnarok New World Quiz Tool',
    heroTitle1: 'Instant Quiz',
    heroTitleAccent: 'Answers',
    heroTitle2: 'from Screen Capture',
    heroDesc: 'Quiz Live OCR captures the question on your screen, reads it with OCR, then matches it against a local question database. Answers appear instantly — no AI, no internet.',
    heroCtaDownload: 'Download Now',
    heroCtaFeatures: 'View Features',
    trialLabel: 'Trial Demo',
    // features
    featuresTitle: 'Key Features',
    featuresDesc: 'Everything you need to answer quizzes fast and accurately.',
    features: [
      { icon: 'scan', title: 'Instant Screen Capture', desc: 'Drag the red box over the question — the app auto-screenshots every second without clicking.' },
      { icon: 'bolt', title: 'Offline OCR', desc: 'Tesseract OCR runs locally on your PC. No connection needed, no AI required.' },
      { icon: 'database', title: 'Local Question Database', desc: 'Questions are matched against a JSON database on your computer. Instant match, instant answer.' },
      { icon: 'shield', title: 'Secure Login', desc: 'FastAPI + PostgreSQL backend. Every login is recorded in the audit log with device info.' },
      { icon: 'rocket', title: 'Two Modes: OCR & AI', desc: 'Live OCR mode is free without AI. AI mode via CommandCode for more accurate answers.' },
      { icon: 'keyboard', title: 'Handy Hotkeys', desc: 'F9 pause/resume, H hide box, Ctrl+S save log. Full control without leaving the keyboard.' },
    ],
    // how it works
    howTitle: 'How It Works',
    howDesc: 'Four steps from opening the app to getting your answer.',
    steps: [
      { num: '01', title: 'Login', desc: 'Open the app, log in with an account created by the admin.' },
      { num: '02', title: 'Select Mode', desc: 'Click SAGE or HOPPY to choose the question database.' },
      { num: '03', title: 'Drag Box', desc: 'Point the red box at the question on screen. OCR runs automatically.' },
      { num: '04', title: 'Answer Appears', desc: 'Question matched → answer shows in the ANSWER panel instantly.' },
    ],
    // pricing / open source & donate
    navPricing: 'Donate',
    pricingTitle: 'Free & Open Source',
    pricingDesc: 'All features free — no fees, no subscriptions. This project is open source — if you like it, you can donate.',
    pricingPromoBadge: '100% OPEN SOURCE',
    pricingPromoEnds: 'No hidden fees — from ReogSoloDev',
    pricingBestValue: 'PAY WHAT YOU WANT',
    pricingFreeTrial: 'Open Source',
    pricingFreeTrialPrice: 'Rp0',
    pricingFreeTrialPeriod: '/forever',
    pricingFreeTrialDesc: 'All features free forever. No fees, no trial, no subscription.',
    pricingTrialBtn: 'Download Free',
    pricingLifetime: 'QRIS Donation',
    pricingLifetimeDesc: 'If you like this project, buy us a coffee via QRIS — any amount. Totally optional.',
    pricingBuyBtn: 'Donate via QRIS',
    pricingQrCaption: 'Scan to donate — any amount',
    pricingDonationName: 'ReogSoloDev · Alfian Dorif Murtadlo',
    pricingIncludesTitle: 'Includes:',
    pricingIncludes: [
      'All features included (OCR + AI mode)',
      'Question database updates',
      'Support via WhatsApp & Discord',
    ],
    // other open source project
    projectsTitle: 'More Open Source from Us',
    projectsDesc: 'RonW-related open source projects we are building.',
    projectRmtBadge: 'UNDER DEVELOPMENT',
    projectRmtName: 'RMT-RONW',
    projectRmtDesc: 'A RonW-related open source project, currently under development.',
    projectRmtRelease: 'Estimated release: 26 October 2026',
    projectRmtSoon: 'Coming Soon',
    // download
    downloadTitle: 'Download Quiz Live OCR',
    downloadDesc: 'Windows desktop app. Download from Google Drive, extract, run. Login with an admin-provided account.',
    downloadBtn: 'Download from Google Drive',
    downloadNoInstall: 'No install needed',
    // contact
    contactTitle: 'Contact Us',
    contactDesc: 'Have questions? Need setup help? Chat with us directly.',
    waLabel: 'WhatsApp',
    waSub: 'Direct chat, fast response',
    discordLabel: 'Discord',
    discordSub: 'Community group & support',
    fbLabel: 'Facebook',
    fbSub: 'Page & info updates',
    // footer
    footerTag: 'Quiz Live OCR — Ragnarok New World',
    footerCopy: '© 2026 REOGSOLODEV. All rights reserved.',
    // placeholder warnings
    envWarningGDrive: '⚠ Google Drive link not set. Edit',
    envWarningEnv: 'in .env',
  },
}

// ---- config dari .env (VITE_* otomatis exposed ke client) ----
const gdriveUrl = computed(() => import.meta.env.VITE_GDRIVE_URL || '#')
const qrisImage = computed(() => import.meta.env.VITE_QRIS_IMAGE || '/qris-v2.png')
const qrisFailed = ref(false)
const onQrisLoad = () => { qrisFailed.value = false }
const onQrisError = () => { qrisFailed.value = true }
const waNumber = computed(() => import.meta.env.VITE_WHATSAPP_NUMBER || '620000000000')
const discordUrl = computed(() => import.meta.env.VITE_DISCORD_URL || '#')
const facebookUrl = computed(() => import.meta.env.VITE_FACEBOOK_URL || '#')

const waLink = computed(() => {
  const num = waNumber.value.replace(/[^0-9]/g, '')
  const msg = locale.value === 'id'
    ? 'Halo%2C%20saya%20mau%20tanya%20soal%20Quiz%20Live%20OCR'
    : 'Hello%2C%20I%20want%20to%20ask%20about%20Quiz%20Live%20OCR'
  return `https://wa.me/${num}?text=${msg}`
})

// cek apakah env masih placeholder (belum diisi)
const isPlaceholder = (val: string) => !val || val.includes('XXXXX') || val === '#'
</script>

<template>
  <!-- ===== NAV ===== -->
  <nav class="fixed top-0 inset-x-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      <a href="#hero" class="flex items-center gap-2.5">
        <img src="/favicon.svg" alt="Logo" class="w-8 h-8" />
        <div class="flex flex-col leading-tight">
          <span class="text-lg font-bold tracking-tight text-white">Quiz Live OCR</span>
          <span class="text-[10px] text-brand-400 font-medium tracking-wide uppercase">Ragnarok New World</span>
        </div>
      </a>
      <div class="hidden md:flex items-center gap-7 text-sm font-medium text-slate-300">
        <a href="#fitur" class="hover:text-white transition-colors">{{ t.navFeatures }}</a>
        <a href="#cara-kerja" class="hover:text-white transition-colors">{{ t.navHowItWorks }}</a>
        <a href="#harga" class="hover:text-white transition-colors">{{ t.navPricing }}</a>
        <a href="#download" class="hover:text-white transition-colors">{{ t.navDownload }}</a>
        <a href="#kontak" class="hover:text-white transition-colors">{{ t.navContact }}</a>
      </div>
      <div class="flex items-center gap-3">
        <!-- language toggle -->
        <button
          @click="locale = locale === 'id' ? 'en' : 'id'"
          class="inline-flex items-center gap-1.5 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition-colors min-h-[40px]"
          :aria-label="`Switch to ${t.langLabel}`"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5h12M9 3v2m1 7l3.5 7M14 12c-1.5-4-5-7-9-7m7.5 7C11 9 7 6 3 6m12 0l4 7m-4-7v7m-5-3.5l3 6.5" />
          </svg>
          {{ t.langLabel }}
        </button>
        <a
          href="#download"
          class="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors min-h-[40px]"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" />
          </svg>
          {{ t.navDownload }}
        </a>
      </div>
    </div>
  </nav>

  <!-- ===== HERO ===== -->
  <section id="hero" class="relative pt-32 pb-20 sm:pt-40 sm:pb-28 overflow-hidden">
    <!-- glow background -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-600/20 rounded-full blur-[120px]"></div>
      <div class="absolute top-40 right-10 w-[300px] h-[300px] bg-purple-600/10 rounded-full blur-[80px]"></div>
    </div>

    <div class="relative max-w-6xl mx-auto px-4 sm:px-6 text-center">
      <span class="inline-flex items-center gap-2 bg-slate-800/70 border border-slate-700 text-brand-200 text-xs font-medium px-3 py-1.5 rounded-full mb-6">
        <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        {{ t.badge }}
      </span>

      <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
        {{ t.heroTitle1 }}
        <span class="bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
          {{ t.heroTitleAccent }}
        </span>
        {{ t.heroTitle2 }}
      </h1>

      <p class="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
        {{ t.heroDesc }}
      </p>

      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
        <a
          :href="gdriveUrl"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-3 bg-brand-600 hover:bg-brand-500 text-white font-semibold px-8 py-3.5 rounded-xl text-base transition-all hover:scale-105 shadow-lg shadow-brand-600/30 min-h-[48px]"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" />
          </svg>
          {{ t.heroCtaDownload }}
        </a>
        <a
          href="#trial"
          class="inline-flex items-center gap-2 text-slate-300 hover:text-white font-medium px-6 py-3.5 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors min-h-[48px]"
        >
          {{ t.heroCtaFeatures }}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </a>
      </div>
    </div>
  </section>

  <!-- ===== TRIAL GIF ===== -->
  <section id="trial" class="pb-20 sm:pb-28 scroll-mt-16">
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="text-center mb-8">
        <span class="inline-flex items-center gap-2 bg-brand-600/15 border border-brand-700/30 text-brand-300 text-xs font-medium px-3 py-1.5 rounded-full">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ t.trialLabel }}
        </span>
      </div>
      <div class="rounded-2xl border border-slate-800 bg-slate-900/50 p-2 shadow-2xl shadow-brand-950/40">
        <div class="rounded-xl overflow-hidden bg-slate-950">
          <img
            src="/trial.gif"
            :alt="t.trialLabel"
            class="w-full h-auto block"
            loading="lazy"
          />
        </div>
      </div>
    </div>
  </section>

  <!-- ===== FITUR ===== -->
  <section id="fitur" class="py-20 sm:py-28 scroll-mt-16">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="text-center mb-14">
        <h2 class="text-3xl sm:text-4xl font-bold text-white">{{ t.featuresTitle }}</h2>
        <p class="mt-4 text-slate-400 max-w-xl mx-auto">{{ t.featuresDesc }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="f in t.features"
          :key="f.title"
          class="group rounded-xl border border-slate-800 bg-slate-900/50 p-6 hover:border-brand-700/50 hover:bg-slate-900 transition-all"
        >
          <div class="w-12 h-12 rounded-lg bg-brand-600/15 text-brand-400 flex items-center justify-center mb-4 group-hover:bg-brand-600/25 transition-colors">
            <!-- icon by type -->
            <svg v-if="f.icon === 'scan'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4h4M4 4v4M20 4h-4M20 4v4M4 20h4M4 20v-4M20 20h-4M20 20v-4M8 12h8" />
            </svg>
            <svg v-if="f.icon === 'bolt'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <svg v-if="f.icon === 'database'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 7c0 1.1 3.6 2 8 2s8-.9 8-2M4 7v10c0 1.1 3.6 2 8 2s8-.9 8-2V7M4 7c0-1.1 3.6-2 8-2s8 .9 8 2" />
            </svg>
            <svg v-if="f.icon === 'shield'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 4v6c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7l8-4z" />
            </svg>
            <svg v-if="f.icon === 'rocket'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 19l3-3m6-8l4-4m-4 4l-4 4m4-4v6m4-4h-6m-2 8l3-3" />
            </svg>
            <svg v-if="f.icon === 'keyboard'" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 5h18v12H3zM7 9h.01M11 9h.01M15 9h.01M7 13h10" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">{{ f.title }}</h3>
          <p class="text-slate-400 text-sm leading-relaxed">{{ f.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== CARA KERJA ===== -->
  <section id="cara-kerja" class="py-20 sm:py-28 scroll-mt-16 bg-slate-900/30 border-y border-slate-800">
    <div class="max-w-6xl mx-auto px-4 sm:px-6">
      <div class="text-center mb-14">
        <h2 class="text-3xl sm:text-4xl font-bold text-white">{{ t.howTitle }}</h2>
        <p class="mt-4 text-slate-400 max-w-xl mx-auto">{{ t.howDesc }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="(s, i) in t.steps"
          :key="s.num"
          class="relative"
        >
          <div v-if="i < t.steps.length - 1" class="hidden lg:block absolute top-8 left-[60%] w-full h-px border-t border-dashed border-slate-700"></div>
          <div class="relative text-center lg:text-left">
            <div class="text-4xl font-extrabold text-brand-600/40 mb-3">{{ s.num }}</div>
            <h3 class="text-lg font-semibold text-white mb-2">{{ s.title }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">{{ s.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== HARGA / PRICING ===== -->
  <section id="harga" class="py-20 sm:py-28 scroll-mt-16">
    <div class="max-w-5xl mx-auto px-4 sm:px-6">
      <div class="text-center mb-10">
        <h2 class="text-3xl sm:text-4xl font-bold text-white">{{ t.pricingTitle }}</h2>
        <p class="mt-4 text-slate-400 max-w-xl mx-auto">{{ t.pricingDesc }}</p>
      </div>

      <!-- promo badge -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center gap-2 bg-amber-500/15 border border-amber-600/30 text-amber-300 text-sm font-semibold px-4 py-2 rounded-full">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {{ t.pricingPromoBadge }}
        </div>
        <p class="mt-3 text-sm text-slate-500">{{ t.pricingPromoEnds }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto items-stretch">
        <!-- Free Trial Card -->
        <div class="rounded-2xl border border-slate-800 bg-slate-900/50 p-8 flex flex-col">
          <div class="w-12 h-12 rounded-xl bg-slate-700/50 text-slate-300 flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">{{ t.pricingFreeTrial }}</h3>
          <div class="mt-4 flex items-baseline gap-1">
            <span class="text-4xl font-extrabold text-white">{{ t.pricingFreeTrialPrice }}</span>
            <span class="text-slate-500 text-sm">{{ t.pricingFreeTrialPeriod }}</span>
          </div>
          <p class="mt-3 text-sm text-slate-400 leading-relaxed">{{ t.pricingFreeTrialDesc }}</p>
          <div class="mt-6 pt-6 border-t border-slate-800 flex-1">
            <p class="text-xs font-medium text-slate-500 mb-3">{{ t.pricingIncludesTitle }}</p>
            <ul class="space-y-2">
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[0] }}
              </li>
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[1] }}
              </li>
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[2] }}
              </li>
            </ul>
          </div>
          <a
            :href="gdriveUrl"
            target="_blank"
            rel="noopener"
            class="mt-6 inline-flex items-center justify-center gap-2 text-slate-200 hover:text-white font-semibold px-6 py-3 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors min-h-[48px]"
          >
            {{ t.pricingTrialBtn }}
          </a>
        </div>

        <!-- Lifetime Promo Card (highlighted) -->
        <div class="relative rounded-2xl border-2 border-brand-600 bg-gradient-to-br from-brand-950/50 to-slate-900/50 p-8 flex flex-col shadow-lg shadow-brand-600/20">
          <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-xs font-bold px-4 py-1 rounded-full whitespace-nowrap">
            {{ t.pricingBestValue }}
          </div>
          <div class="w-12 h-12 rounded-xl bg-brand-600/20 text-brand-400 flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 4v6c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7l8-4z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">{{ t.pricingLifetime }}</h3>
          <div class="mt-4 flex items-baseline gap-1">
            <span class="text-4xl font-extrabold text-white">Seikhlasnya</span>
          </div>
          <p class="mt-3 text-sm text-slate-400 leading-relaxed">{{ t.pricingLifetimeDesc }}</p>
          <div class="mt-6 flex justify-center">
            <div class="w-44 min-h-[11rem] rounded-xl bg-white border border-slate-700 flex items-center justify-center overflow-hidden">
              <img :src="qrisImage" alt="QRIS Donation" class="w-full h-auto object-contain" :class="qrisFailed ? 'hidden' : ''" @load="onQrisLoad" @error="onQrisError" />
              <div class="qris-fallback" :class="qrisFailed ? 'flex' : 'hidden'" style="flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 1rem;">
                <svg class="w-10 h-10 text-slate-400 mb-2" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM14.625 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0114.625 9.375v-4.5z" /><path stroke-linecap="round" stroke-linejoin="round" d="M14.625 14.625v4.5c0 .621.504 1.125 1.125 1.125h4.5c.621 0 1.125-.504 1.125-1.125v-4.5c0-.621-.504-1.125-1.125-1.125h-4.5a1.125 1.125 0 00-1.125 1.125z" /></svg>
                <span class="text-xs text-slate-500 font-medium">QRIS</span>
                <span class="text-[11px] text-slate-400 mt-1">{{ t.pricingDonationName }}</span>
              </div>
            </div>
          </div>
          <p class="mt-3 text-xs text-slate-500 text-center">{{ t.pricingQrCaption }}</p>
          <div class="mt-6 pt-6 border-t border-slate-800 flex-1">
            <p class="text-xs font-medium text-slate-500 mb-3">{{ t.pricingIncludesTitle }}</p>
            <ul class="space-y-2">
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[0] }}
              </li>
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[1] }}
              </li>
              <li class="flex items-start gap-2 text-sm text-slate-400">
                <svg class="w-4 h-4 text-green-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {{ t.pricingIncludes[2] }}
              </li>
            </ul>
          </div>
          <a
            :href="qrisImage"
            target="_blank"
            rel="noopener"
            class="mt-6 w-full inline-flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 text-white font-bold px-6 py-3 rounded-xl transition-colors min-h-[48px]"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 013.75 9.375v-4.5zM3.75 14.625c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5a1.125 1.125 0 01-1.125-1.125v-4.5zM14.625 4.875c0-.621.504-1.125 1.125-1.125h4.5c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125h-4.5A1.125 1.125 0 0114.625 9.375v-4.5z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.625 14.625v4.5c0 .621.504 1.125 1.125 1.125h4.5c.621 0 1.125-.504 1.125-1.125v-4.5c0-.621-.504-1.125-1.125-1.125h-4.5a1.125 1.125 0 00-1.125 1.125z" />
            </svg>
            {{ t.pricingBuyBtn }}
          </a>
        </div>

        <!-- RMT-RONW Card (under development) -->
        <div class="rounded-2xl border border-dashed border-slate-700 bg-slate-900/30 p-8 flex flex-col relative opacity-90">
          <div class="absolute -top-3 left-6 inline-flex items-center gap-1.5 bg-amber-500/15 border border-amber-600/40 text-amber-300 text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wide">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.736l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.736 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
            </svg>
            {{ t.projectRmtBadge }}
          </div>
          <div class="w-12 h-12 rounded-xl bg-slate-700/50 text-slate-300 flex items-center justify-center mb-5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">{{ t.projectRmtName }}</h3>
          <div class="mt-4">
            <span class="inline-block text-2xl font-extrabold text-slate-400">{{ t.projectRmtSoon }}</span>
          </div>
          <p class="mt-3 text-sm text-slate-400 leading-relaxed">{{ t.projectRmtDesc }}</p>
          <p class="mt-4 pt-4 border-t border-slate-800 flex-1 text-sm text-slate-500">
            {{ t.projectRmtRelease }}
          </p>
          <span class="mt-6 w-full inline-flex items-center justify-center gap-2 bg-slate-800/60 text-slate-500 font-bold px-6 py-3 rounded-xl cursor-not-allowed border border-slate-700/50 min-h-[48px]">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ t.projectRmtSoon }}
          </span>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== DOWNLOAD ===== -->
  <section id="download" class="py-20 sm:py-28 scroll-mt-16">
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="relative rounded-2xl border border-brand-700/30 bg-gradient-to-br from-brand-950/40 to-slate-900/40 p-8 sm:p-12 text-center overflow-hidden">
        <div class="absolute inset-0 pointer-events-none">
          <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[200px] bg-brand-600/15 rounded-full blur-[80px]"></div>
        </div>

        <div class="relative">
          <div class="w-16 h-16 mx-auto rounded-2xl bg-brand-600/20 text-brand-400 flex items-center justify-center mb-6">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" />
            </svg>
          </div>

          <h2 class="text-3xl sm:text-4xl font-bold text-white">{{ t.downloadTitle }}</h2>
          <p class="mt-4 text-slate-400 max-w-lg mx-auto">{{ t.downloadDesc }}</p>

          <div class="mt-6 flex flex-wrap items-center justify-center gap-3 text-sm text-slate-500">
            <span class="inline-flex items-center gap-1.5">
              <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Windows 10/11
            </span>
            <span class="inline-flex items-center gap-1.5">
              <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              ~63 MB
            </span>
            <span class="inline-flex items-center gap-1.5">
              <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              {{ t.downloadNoInstall }}
            </span>
          </div>

          <a
            :href="gdriveUrl"
            target="_blank"
            rel="noopener"
            class="mt-8 inline-flex items-center gap-3 bg-brand-600 hover:bg-brand-500 text-white font-bold px-8 py-4 rounded-xl text-lg transition-all hover:scale-105 shadow-lg shadow-brand-600/30 min-h-[52px]"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" />
            </svg>
            {{ t.downloadBtn }}
          </a>

          <p v-if="isPlaceholder(gdriveUrl)" class="mt-4 text-xs text-amber-400/80">
            {{ t.envWarningGDrive }} <code class="bg-slate-800 px-1.5 py-0.5 rounded">frontend/.env</code> → <code class="bg-slate-800 px-1.5 py-0.5 rounded">VITE_GDRIVE_URL</code>
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== KONTAK ===== -->
  <section id="kontak" class="py-20 sm:py-28 scroll-mt-16 bg-slate-900/30 border-t border-slate-800">
    <div class="max-w-4xl mx-auto px-4 sm:px-6">
      <div class="text-center mb-12">
        <h2 class="text-3xl sm:text-4xl font-bold text-white">{{ t.contactTitle }}</h2>
        <p class="mt-4 text-slate-400">{{ t.contactDesc }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <!-- WhatsApp -->
        <a
          :href="waLink"
          target="_blank"
          rel="noopener"
          class="group flex flex-col items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-8 hover:border-green-600/50 hover:bg-slate-900 transition-all"
        >
          <div class="w-14 h-14 rounded-xl bg-green-600/15 text-green-400 flex items-center justify-center group-hover:bg-green-600/25 transition-colors">
            <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.47 14.38c-.3-.15-1.77-.87-2.04-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.87 1.22 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.62.71.23 1.36.2 1.87.12.57-.08 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35z"/>
              <path d="M12 2C6.48 2 2 6.48 2 12c0 1.77.46 3.43 1.27 4.87L2 22l5.25-1.38A9.9 9.9 0 0012 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18.2c-1.5 0-2.9-.4-4.1-1.1l-.3-.17-3.12.82.83-3.04-.2-.31A8.16 8.16 0 013.8 12c0-4.53 3.67-8.2 8.2-8.2s8.2 3.67 8.2 8.2-3.67 8.2-8.2 8.2z"/>
            </svg>
          </div>
          <div class="text-center">
            <div class="font-semibold text-white">{{ t.waLabel }}</div>
            <div class="text-sm text-slate-400 mt-1">{{ t.waSub }}</div>
          </div>
          <p v-if="isPlaceholder(waNumber)" class="text-xs text-amber-400/70">Isi VITE_WHATSAPP_NUMBER di .env</p>
        </a>

        <!-- Discord -->
        <a
          :href="discordUrl"
          target="_blank"
          rel="noopener"
          class="group flex flex-col items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-8 hover:border-indigo-500/50 hover:bg-slate-900 transition-all"
        >
          <div class="w-14 h-14 rounded-xl bg-indigo-500/15 text-indigo-400 flex items-center justify-center group-hover:bg-indigo-500/25 transition-colors">
            <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.32 4.37A19.79 19.79 0 0016.56 3c-.18.32-.39.74-.53 1.07-1.59-.24-3.16-.24-4.71 0-.15-.33-.36-.75-.54-1.07-1.28.22-2.5.6-3.65 1.37C3.94 7.47 3.08 10.58 3 13.63c1.7.78 3.34 1.26 4.95 1.57.4-.54.76-1.1 1.07-1.7-.59-.22-1.15-.5-1.68-.81.14-.1.28-.21.41-.32 3.21 1.48 6.69 1.48 9.86 0 .14.11.27.22.41.32-.53.31-1.09.59-1.68.81.31.6.67 1.16 1.07 1.7 1.61-.31 3.25-.79 4.95-1.57-.1-3.05-.96-6.16-3.04-9.26zM9.18 12.09c-.95 0-1.73-.87-1.73-1.94 0-1.07.76-1.94 1.73-1.94.97 0 1.75.88 1.73 1.94 0 1.07-.77 1.94-1.73 1.94zm5.64 0c-.95 0-1.73-.87-1.73-1.94 0-1.07.76-1.94 1.73-1.94.97 0 1.75.88 1.73 1.94 0 1.07-.76 1.94-1.73 1.94z"/>
            </svg>
          </div>
          <div class="text-center">
            <div class="font-semibold text-white">{{ t.discordLabel }}</div>
            <div class="text-sm text-slate-400 mt-1">{{ t.discordSub }}</div>
          </div>
          <p v-if="isPlaceholder(discordUrl)" class="text-xs text-amber-400/70">Isi VITE_DISCORD_URL di .env</p>
        </a>

        <!-- Facebook -->
        <a
          :href="facebookUrl"
          target="_blank"
          rel="noopener"
          class="group flex flex-col items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-8 hover:border-blue-500/50 hover:bg-slate-900 transition-all"
        >
          <div class="w-14 h-14 rounded-xl bg-blue-500/15 text-blue-400 flex items-center justify-center group-hover:bg-blue-500/25 transition-colors">
            <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.02 4.39 11.01 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.95.93-1.95 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.08 24 18.09 24 12.07z"/>
            </svg>
          </div>
          <div class="text-center">
            <div class="font-semibold text-white">{{ t.fbLabel }}</div>
            <div class="text-sm text-slate-400 mt-1">{{ t.fbSub }}</div>
          </div>
          <p v-if="isPlaceholder(facebookUrl)" class="text-xs text-amber-400/70">Isi VITE_FACEBOOK_URL di .env</p>
        </a>
      </div>
    </div>
  </section>

  <!-- ===== FOOTER ===== -->
  <footer class="border-t border-slate-800 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2.5">
        <img src="/favicon.svg" alt="Logo" class="w-7 h-7" />
        <span class="text-sm text-slate-400">{{ t.footerTag }}</span>
      </div>
      <div class="flex items-center gap-5">
        <a :href="waLink" target="_blank" rel="noopener" class="text-slate-500 hover:text-green-400 transition-colors" aria-label="WhatsApp">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.47 14.38c-.3-.15-1.77-.87-2.04-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.87 1.22 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.62.71.23 1.36.2 1.87.12.57-.08 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35z"/>
            <path d="M12 2C6.48 2 2 6.48 2 12c0 1.77.46 3.43 1.27 4.87L2 22l5.25-1.38A9.9 9.9 0 0012 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18.2c-1.5 0-2.9-.4-4.1-1.1l-.3-.17-3.12.82.83-3.04-.2-.31A8.16 8.16 0 013.8 12c0-4.53 3.67-8.2 8.2-8.2s8.2 3.67 8.2 8.2-3.67 8.2-8.2 8.2z"/>
          </svg>
        </a>
        <a :href="discordUrl" target="_blank" rel="noopener" class="text-slate-500 hover:text-indigo-400 transition-colors" aria-label="Discord">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M20.32 4.37A19.79 19.79 0 0016.56 3c-.18.32-.39.74-.53 1.07-1.59-.24-3.16-.24-4.71 0-.15-.33-.36-.75-.54-1.07-1.28.22-2.5.6-3.65 1.37C3.94 7.47 3.08 10.58 3 13.63c1.7.78 3.34 1.26 4.95 1.57.4-.54.76-1.1 1.07-1.7-.59-.22-1.15-.5-1.68-.81.14-.1.28-.21.41-.32 3.21 1.48 6.69 1.48 9.86 0 .14.11.27.22.41.32-.53.31-1.09.59-1.68.81.31.6.67 1.16 1.07 1.7 1.61-.31 3.25-.79 4.95-1.57-.1-3.05-.96-6.16-3.04-9.26zM9.18 12.09c-.95 0-1.73-.87-1.73-1.94 0-1.07.76-1.94 1.73-1.94.97 0 1.75.88 1.73 1.94 0 1.07-.77 1.94-1.73 1.94zm5.64 0c-.95 0-1.73-.87-1.73-1.94 0-1.07.76-1.94 1.73-1.94.97 0 1.75.88 1.73 1.94 0 1.07-.76 1.94-1.73 1.94z"/>
          </svg>
        </a>
        <a :href="facebookUrl" target="_blank" rel="noopener" class="text-slate-500 hover:text-blue-400 transition-colors" aria-label="Facebook">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07c0 6.02 4.39 11.01 10.13 11.93v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.69 4.53-4.69 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.95.93-1.95 1.89v2.25h3.33l-.53 3.49h-2.8V24C19.61 23.08 24 18.09 24 12.07z"/>
          </svg>
        </a>
      </div>
      <p class="text-xs text-slate-600">
        © 2026
        <a href="https://reogsolodev.com" target="_blank" rel="noopener"
           class="text-slate-400 hover:text-slate-100 underline underline-offset-2 transition-colors">REOGSOLODEV</a>.
        All rights reserved.
      </p>
    </div>
  </footer>
</template>
