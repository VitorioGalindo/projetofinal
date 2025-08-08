# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

## Run Locally

**Prerequisites:**  Node.js


1. Instale as dependências (este comando na raiz instala também o conteúdo de `frontend`):
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`
4. Na raiz do projeto, execute os testes do frontend (uma única vez, sem modo watch):
   `npm test`
