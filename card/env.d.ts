/// <reference types="vite/client" />
declare module '~icons/*';
declare module '*.css?inline' {
  const css: string;
  export default css;
}
