/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GDRIVE_URL: string
  readonly VITE_WHATSAPP_NUMBER: string
  readonly VITE_DISCORD_URL: string
  readonly VITE_FACEBOOK_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
