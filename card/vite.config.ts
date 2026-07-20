import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
import AutoImport from 'unplugin-auto-import/vite';
import IconsResolver from 'unplugin-icons/resolver';
import Icons from 'unplugin-icons/vite';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('ha-'),
        },
      },
    }),
    Icons({ compiler: 'vue3' }),
    tailwindcss(),
    AutoImport({
      include: [/\.[tj]sx?$/, /\.vue$/, /\.vue\?vue/],
      vueTemplate: true,
      dts: fileURLToPath(new URL('./src/types/auto-imports.d.ts', import.meta.url)),
      imports: ['vue', '@vueuse/core'],
    }),
    Components({
      extensions: ['vue'],
      include: [/\.vue$/, /\.vue\?vue/],
      dts: fileURLToPath(new URL('./src/types/components.d.ts', import.meta.url)),
      resolvers: [IconsResolver()],
    }),
  ],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    dedupe: ['vue', 'primevue', '@primeuix/themes', '@primeuix/utils', '@vueuse/core'],
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
  build: {
    target: 'es2022',
    outDir: '../custom_components/cameraui/www',
    emptyOutDir: true,
    cssCodeSplit: false,
    lib: {
      entry: 'src/main.ts',
      formats: ['es'],
      fileName: () => 'cameraui-card.js',
    },
  },
});
