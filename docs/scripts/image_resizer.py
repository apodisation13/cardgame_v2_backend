import os
from PIL import Image
from pathlib import Path
import sys


class SmartImageOptimizer:
    def __init__(self):
        self.config = {
            'formats': {
                'original': 'webp',
                'tablet': 'webp',
                'phone': 'webp'
            },
            'sizes': {
                'tablet': 0.5,
                'phone': 0.2,
            },
            'quality': {
                'original': 90,
                'tablet': 80,
                'phone': 70
            },
        }

    def optimize_image(self, image_path):
        """
        Оптимизирует изображение и создает версии для разных устройств
        """
        try:
            img_path = Path(image_path)
            if not img_path.exists():
                print(f"Файл не найден: {image_path}")
                return {}

            # Открываем изображение
            with Image.open(img_path) as img:
                print(img.size)


                # Конвертируем в RGB если нужно (для JPG/WebP)
                original_mode = img.mode
                print(62, original_mode)
                if self.config['formats']['original'] in ['jpg', 'jpeg', 'webp']:
                    print(64)

                filename = img_path.stem

                print(83, filename)

                # Создаем все версии изображения
                image_paths = {}

                for version in ['original', 'tablet', 'phone']:
                    # Определяем выходной формат
                    output_format = self.config['formats'][version].upper()
                    if output_format == 'JPG':
                        output_format = 'JPEG'

                    # Создаем новое имя файла
                    new_filename = f"{filename}_{version}.{self.config['formats'][version]}"
                    output_path = Path(image_path).parent / new_filename
                    print(102, new_filename, output_path)

                    if version == 'original':
                        print(105)
                        self._save_image(
                            img, output_path, output_format,
                            quality=self.config['quality'][version]
                        )
                    else:
                        print(119)
                        percent = self.config['sizes'][version]
                        new_size = (
                            int(img.width * percent),
                            int(img.height * percent)
                        )
                        # Изменяем размер
                        img_resized = img.resize(
                            new_size,
                            Image.Resampling.LANCZOS  # Качественный ресайз
                        )
                        print(142)

                        # Сохраняем
                        self._save_image(
                            img_resized, output_path, output_format,
                            quality=self.config['quality'][version]
                        )

                    # Сохраняем относительный путь для БД
                    relative_path = f"media/{new_filename}" if version != 'original' else str(img_path)
                    image_paths[version] = relative_path
                    print(153, relative_path)
                    print(f"  Создано: {version} ({new_size if version != 'original' else img.size}) - {output_path}")

                return image_paths

        except Exception as e:
            print(f"Ошибка при обработке {image_path}: {e}")
            return {}

    def _save_image(self, image, output_path, format, quality):
        """Сохраняет изображение с нужными параметрами"""
        save_args = {
            'format': format,
            'quality': quality,
            'optimize': True
        }

        # Добавляем параметры для WebP
        if format == 'WEBP':
            save_args['method'] = 6  # Уровень сжатия (0-6)

        # Сохраняем в прогрессивном формате для JPG
        if format == 'JPEG':
            save_args['progressive'] = True

        image.save(output_path, **save_args)


def main():
    optimizer = SmartImageOptimizer()

    # Обработка всех изображений в папке
    source_dir = Path("../../shared_static/media")
    for img_file in list(source_dir.rglob("*.jpg")):
        print(f"Обработка: {img_file.name}")
        result = optimizer.optimize_image(img_file)
        print(f"  Результат: {result}")
        print()


if __name__ == "__main__":
    main()
