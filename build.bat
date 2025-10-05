@echo off
echo 🐍 Instalando dependências Python...
pip install -r requirements.txt

echo 📦 Instalando dependências Node...
npm install

echo 🎨 Compilando Tailwind CSS...
npm run build

echo 📁 Coletando arquivos estáticos do Django...
python manage.py collectstatic --noinput

echo 🔧 Aplicando migrações...
python manage.py migrate

echo ✅ Build finalizado com sucesso!
pause
