import sys
import subprocess
import os
import logging
import shutil
import argparse
from io import BytesIO
from queue import Queue
import imagehash
from tqdm import tqdm
from colorama import Fore, Style

def check_and_install_packages(requirements_file):
    """Controlla e installa i pacchetti dal file requirements.txt."""
    with open(requirements_file, 'r') as file:
        packages = [pkg.strip() for pkg in file.readlines() if pkg.strip()]

    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'show', package.split('==')[0]], check=True, stdout=subprocess.DEVNULL)
            print(f"\033[92m{package} è già installato.\033[0m")
        except subprocess.CalledProcessError:
            print(f"\033[93m{package} non è installato. Installazione in corso...\033[0m")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            except Exception as e:
                print(f"\033[91mErrore durante l'installazione di {package}: {str(e)}\033[0m")

def import_libraries():
    """Importa le librerie necessarie e installa quelle mancanti."""
    try:
        import fitz
        from PIL import Image, ImageOps, ImageFilter
        import imagehash
        from tqdm import tqdm
        from colorama import Fore, Style
    except ImportError as e:
        missing_package = str(e).split()[-1]
        print(f"\033[91mLibreria mancante: {missing_package}. Installazione in corso...\033[0m")
        check_and_install_packages('requirements.txt')
        import_libraries()  # Ripeti l'importazione delle librerie dopo l'installazione
        import fitz
        from PIL import Image, ImageOps, ImageFilter
        import imagehash
        from tqdm import tqdm
        from colorama import Fore, Style

def are_images_similar(img1, img2, threshold=0.85):
    """Verifica se due immagini sono simili basandosi su hash percettivo."""
    hash1 = imagehash.phash(img1, hash_size=8)
    hash2 = imagehash.phash(img2, hash_size=8)
    similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
    return similarity >= threshold

def crop_image(img, ratio=1/7):
    """Taglia l'immagine secondo il rapporto specificato e la converte in bianco e nero."""
    from PIL import ImageOps, ImageFilter
    width, height = img.size
    top = int(height * ratio)
    cropped_img = img.crop((0, 0, width, top))
    bw_img = ImageOps.grayscale(cropped_img)
    blurred_img = bw_img.filter(ImageFilter.GaussianBlur(radius=3.5))
    return blurred_img

def cleanup_directory(directory):
    """Elimina tutti i file e le cartelle nella directory specificata."""
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def process_pdfs(pdf_dir, img_dir, docs_dir, log_dir, similarity_threshold=0.8, ratio=1/5):
    """Processa i PDF e organizza i documenti in base alla similarità delle immagini."""
    from PIL import Image
    import fitz
    pdf_paths = {}
    image_queue = Queue()
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    total_pdfs = len(pdf_files)

    with tqdm(total=total_pdfs, desc=f"{Fore.GREEN}Percentuale di lavoro: {Style.RESET_ALL}", unit="pdf") as pbar:
        for filename in pdf_files:
            pdf_path = os.path.join(pdf_dir, filename)
            logging.info(f'Processo \'{filename}\'')
            try:
                pdf_document = fitz.open(pdf_path)
                first_page = pdf_document.load_page(0)
                pix = first_page.get_pixmap()
                img_bytes = pix.tobytes()
                
                with Image.open(BytesIO(img_bytes)) as img:
                    cropped_img = crop_image(img, ratio=ratio)
                    
                    if image_queue.empty():
                        key = '001'
                        pdf_paths[key] = [pdf_path]
                        img_path = os.path.join(img_dir, f'{key}.png')
                        cropped_img.save(img_path)
                        image_queue.put((key, cropped_img))
                        logging.info(f'Aggiunta nuova chiave \'{key}\' e percorso: \'{pdf_path}\'')
                    else:
                        found_similar = False
                        for q_key, q_img in list(image_queue.queue):
                            if are_images_similar(q_img, cropped_img, threshold=similarity_threshold):
                                pdf_paths[q_key].append(pdf_path)
                                found_similar = True
                                logging.info(f'Trovata immagine simile alla chiave \'{q_key}\'. Aggiunto percorso: {pdf_path}')
                                break

                        if not found_similar:
                            new_key = f'{len(pdf_paths) + 1:03}'
                            pdf_paths[new_key] = [pdf_path]
                            img_path = os.path.join(img_dir, f'{new_key}.png')
                            cropped_img.save(img_path)
                            image_queue.put((new_key, cropped_img))
                            logging.info(f'Aggiunta nuova chiave \'{new_key}\' e percorso: \'{pdf_path}\'')

            except Exception as e:
                logging.error(f'Errore nel processare \'{filename}\': "{str(e)}"')
            finally:
                pdf_document.close()

            pbar.update(1)
            pbar.set_postfix({"Chiavi": len(pdf_paths), "PDF": sum(len(paths) for paths in pdf_paths.values())}, refresh=True)

    for key, paths in pdf_paths.items():
        key_docs_dir = os.path.join(docs_dir, key)
        os.makedirs(key_docs_dir, exist_ok=True)
        for path in paths:
            filename = os.path.basename(path)
            new_path = os.path.join(key_docs_dir, filename)
            try:
                shutil.move(path, new_path)
                logging.info(f'Spostato \'{filename}\' in \'{key_docs_dir}\'')
            except Exception as e:
                logging.error(f'Errore nello spostamento di \'{filename}\' in \'{key_docs_dir}\': "{str(e)}"')

    cleanup_directory(img_dir)

    final_log_file_path = os.path.join(log_dir, 'final_report.log')
    with open(final_log_file_path, 'w') as f:
        for foldername, subfolders, filenames in os.walk(docs_dir):
            num_pdfs_in_folder = len([f for f in filenames if f.lower().endswith('.pdf')])
            f.write(f"{foldername}: {num_pdfs_in_folder} PDF\n")
            logging.info(f"{foldername}: {num_pdfs_in_folder} PDF")

    logging.info("Processo completato.")

def main(requirements_file, source_dir, similarity_threshold=0.8, ratio=1/5):
    """Funzione principale che gestisce l'intero processo."""
    import_libraries()  # Assicurati che le librerie siano importate e installate
    import imagehash
    from tqdm import tqdm
    from colorama import Fore, Style

    cwd = os.getcwd()
    log_dir = os.path.join(cwd, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'process_log.log')
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    img_dir = os.path.join(cwd, 'img')
    os.makedirs(img_dir, exist_ok=True)

    docs_dir = os.path.join(cwd, 'docs')
    os.makedirs(docs_dir, exist_ok=True)

    data_dir = os.path.join(cwd, 'data')
    os.makedirs(data_dir, exist_ok=True)

    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(data_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    process_pdfs(data_dir, img_dir, docs_dir, log_dir, similarity_threshold, ratio)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Processa i PDF e li organizza per azienda')
    parser.add_argument('-s', '--source', required=True, help='Directory contenente i PDF')
    parser.add_argument('-r', '--requirements', default='requirements.txt', help='File di testo contenente i requisiti')
    parser.add_argument('--similarity_threshold', type=float, default=0.8, help='Percentuale di similarità (default: 0.8)')
    parser.add_argument('--ratio', type=float, default=1/7, help='Rapporto di taglio dell\'immagine del PDF')
    
    args = parser.parse_args()
    main(args.requirements, args.source, args.similarity_threshold, args.ratio)
