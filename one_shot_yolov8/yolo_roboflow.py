# %% [markdown]
# [![Roboflow Notebooks](https://media.roboflow.com/notebooks/template/bannertest2-2.png?ik-sdk-version=javascript-1.4.3&updatedAt=1672932710194)](https://github.com/roboflow/notebooks)
# 
# # How to Auto Train YOLOv8 Model with Autodistill
# 
# Autodistill uses big, slower foundation models to train small, faster supervised models. Using `autodistill`, you can go from unlabeled images to inference on a custom model running at the edge with no human intervention in between.
# 
# ![Autodistill Steps](https://media.roboflow.com/open-source/autodistill/steps.jpg)
# 
# As foundation models get better and better they will increasingly be able to augment or replace humans in the labeling process. We need tools for steering, utilizing, and comparing these models. Additionally, these foundation models are big, expensive, and often gated behind private APIs. For many production use-cases, we need models that can run cheaply and in realtime at the edge.
# 
# ![Autodistill Connections](https://media.roboflow.com/open-source/autodistill/connections.jpg)
# 
# ## Steps in this Tutorial
# 
# In this tutorial, we are going to cover:
# 
# - Before you start
# - Image dataset preperation
# - Autolabel dataset
# - Train target model
# - Evaluate target model
# - Run video inference
# - Upload dataset and model to Roboflow (comming soon)
# 
# ## 🔥 Let's begin!
# 

# %% [markdown]
# ## ⚡ Before you start
# 
# Let's make sure that we have access to GPU. We can use `nvidia-smi` command to do that. In case of any problems navigate to `Edit` -> `Notebook settings` -> `Hardware accelerator`, set it to `GPU`, and then click `Save`.

# %%
!nvidia-smi

# %% [markdown]
# ## 🧪 Install autodistill
# 
# **NOTE:** Autodistill is an ecosystem for using big, slower foundation models to train small, faster supervised models. Each Base, as well as the Target model, has its own separate repository and pip package.

# %%
!pip install -q \
autodistill \
autodistill-grounded-sam \
autodistill-yolov8 \
roboflow \
supervision==0.9.0

# %% [markdown]
# **NOTE:** To make it easier for us to manage datasets, images and models we create a `HOME` constant.

# %%
import os
HOME = os.getcwd()
print(HOME)

# %% [markdown]
# ## 🖼️ Image dataset preperation
# 
# **NOTE:** To use Autodistill all you need to have is a folder of images that you want to automatically annotate, and use for target model training.

# %%
!mkdir {HOME}/images

# %% [markdown]
# ## Download Images
# 
# Below, we provide two methods of retrieving images for use with Autodistill:
# 
# 1. Download a dataset with images from Roboflow, and;
# 2. Download a raw video and split it up into images.
# 
# For this guide, we will be using a raw video to train our model.

# %% [markdown]
# ### Download Images from Roboflow
# 
# You can download datasets from Roboflow using the below lines of code. You can download datasets associated with your account, or any of the 200,000+ public datasets on [Roboflow Universe](https://universe.roboflow.com/). To download a dataset from Roboflow, you will need a [free Roboflow account](https://app.roboflow.com).
# 
# You need to paste in a URL to a full model, like so:
# 
# ```
# https://universe.roboflow.com/mohamed-traore-2ekkp/taco-trash-annotations-in-context/model/16
# ```
# 
# To find a model URL, go to a dataset page on Universe (i.e. the [TACO dataset](https://universe.roboflow.com/mohamed-traore-2ekkp/taco-trash-annotations-in-context/)), then click "Model" in the sidebar to view the latest model version. Copy the page URL, then paste it into the `download_dataset()` function below.
# 
# ![Universe model link](https://media.roboflow.com/universe_deploy_tab.png)
# 
# Uncomment the lines of code below to use the Roboflow dataset upload.

# %%
# import roboflow

# roboflow.login()

# dataset = roboflow.download_dataset(dataset_url="https://universe.roboflow.com/mohamed-traore-2ekkp/taco-trash-annotations-in-context/model/16", model_format="yolov8")

# %% [markdown]
# Once you have downloaded your dataset, move all of the images from the `train` set in your downloaded dataset into the `images/` directory we created earlier:

# %%
# %mv {HOME}/<dataset-name>/train/* {HOME}/images

# %% [markdown]
# Now we are ready to start using Autodistill!

# %% [markdown]
# ### Download raw videos
# 
# **NOTE:** In this tutorial, we will start with a directory containing video files and I will show you how to turn it into a ready-to-use collection of images. If you are working with your images, you can skip this part.

# %%
!mkdir {HOME}/videos
%cd {HOME}/videos

# download zip file containing videos
!wget https://media.roboflow.com/milk.zip

# unzip videos
!unzip milk.zip

# %% [markdown]
# ### Convert videos into images
# 
# **NOTE:** Now, let's convert videos into images. By default, the code below saves every `10th` frame from each video. You can change this by manipulating the value of the `FRAME_STRIDE` parameter.

# %%
VIDEO_DIR_PATH = f"{HOME}/videos"
IMAGE_DIR_PATH = f"{HOME}/images"
FRAME_STRIDE = 10
os.VIDEO_DIR_PATH.lstrip()
# %% [markdown]
# **NOTE:** Notice that we put two of our videos aside so that we can use them at the end of the notebook to evaluate our model.

# %%
import supervision as sv
from tqdm.notebook import tqdm

video_paths = sv.list_files_with_extensions(
    directory=VIDEO_DIR_PATH,
    extensions=["mov", "mp4"])

TEST_VIDEO_PATHS, TRAIN_VIDEO_PATHS = video_paths[:2], video_paths[2:]

for video_path in tqdm(TRAIN_VIDEO_PATHS):
    video_name = video_path.stem
    image_name_pattern = video_name + "-{:05d}.png"
    with sv.ImageSink(target_dir_path=IMAGE_DIR_PATH, image_name_pattern=image_name_pattern) as sink:
        for image in sv.get_video_frames_generator(source_path=str(video_path), stride=FRAME_STRIDE):
            sink.save_image(image=image)

# %% [markdown]
# ### Display image sample
# 
# **NOTE:** Before we start building a model with autodistill, let's make sure we have everything we need.

# %%
import supervision as sv

image_paths = sv.list_files_with_extensions(
    directory=IMAGE_DIR_PATH,
    extensions=["png", "jpg", "jpg"])

print('image count:', len(image_paths))

# %% [markdown]
# **NOTE:** We can also plot sample of our image dataset.

# %%
IMAGE_DIR_PATH = f"{HOME}/images"
SAMPLE_SIZE = 16
SAMPLE_GRID_SIZE = (4, 4)
SAMPLE_PLOT_SIZE = (16, 16)

# %%
import cv2
import supervision as sv

titles = [
    image_path.stem
    for image_path
    in image_paths[:SAMPLE_SIZE]]
images = [
    cv2.imread(str(image_path))
    for image_path
    in image_paths[:SAMPLE_SIZE]]

sv.plot_images_grid(images=images, titles=titles, grid_size=SAMPLE_GRID_SIZE, size=SAMPLE_PLOT_SIZE)

# %% [markdown]
# ## 🏷️ Autolabel dataset

# %% [markdown]
# ### Define ontology
# 
# **Ontology** - an Ontology defines how your Base Model is prompted, what your Dataset will describe, and what your Target Model will predict. A simple Ontology is the CaptionOntology which prompts a Base Model with text captions and maps them to class names. Other Ontologies may, for instance, use a CLIP vector or example images instead of a text caption.

# %%
from autodistill.detection import CaptionOntology

ontology=CaptionOntology({
    "milk bottle": "bottle",
    "blue cap": "cap"
})

# %% [markdown]
# ### Initiate base model and autolabel
# 
# **Base Model** - A Base Model is a large foundation model that knows a lot about a lot. Base models are often multimodal and can perform many tasks. They're large, slow, and expensive. Examples of Base Models are GroundedSAM and GPT-4's upcoming multimodal variant. We use a Base Model (along with unlabeled input data and an Ontology) to create a Dataset.

# %%
DATASET_DIR_PATH = f"{HOME}/dataset"

# %% [markdown]
# **NOTE:** Base Models are slow... Make yourself a coffee, autolabeing may take a while. ☕

# %%
from autodistill_grounded_sam import GroundedSAM

base_model = GroundedSAM(ontology=ontology)
dataset = base_model.label(
    input_folder=IMAGE_DIR_PATH,
    extension=".png",
    output_folder=DATASET_DIR_PATH)

# %% [markdown]
# ### Display dataset sample
# 
# **Dataset** - a Dataset is a set of auto-labeled data that can be used to train a Target Model. It is the output generated by a Base Model.

# %%
ANNOTATIONS_DIRECTORY_PATH = f"{HOME}/dataset/train/labels"
IMAGES_DIRECTORY_PATH = f"{HOME}/dataset/train/images"
DATA_YAML_PATH = f"{HOME}/dataset/data.yaml"

# %%
import supervision as sv

dataset = sv.DetectionDataset.from_yolo(
    images_directory_path=IMAGES_DIRECTORY_PATH,
    annotations_directory_path=ANNOTATIONS_DIRECTORY_PATH,
    data_yaml_path=DATA_YAML_PATH)

len(dataset)

# %%
import supervision as sv

image_names = list(dataset.images.keys())[:SAMPLE_SIZE]

mask_annotator = sv.MaskAnnotator()
box_annotator = sv.BoxAnnotator()

images = []
for image_name in image_names:
    image = dataset.images[image_name]
    annotations = dataset.annotations[image_name]
    labels = [
        dataset.classes[class_id]
        for class_id
        in annotations.class_id]
    annotates_image = mask_annotator.annotate(
        scene=image.copy(),
        detections=annotations)
    annotates_image = box_annotator.annotate(
        scene=annotates_image,
        detections=annotations,
        labels=labels)
    images.append(annotates_image)

sv.plot_images_grid(
    images=images,
    titles=image_names,
    grid_size=SAMPLE_GRID_SIZE,
    size=SAMPLE_PLOT_SIZE)

# %% [markdown]
# ## 🔥 Train target model - YOLOv8
# 
# **Target Model** - a Target Model is a supervised model that consumes a Dataset and outputs a distilled model that is ready for deployment. Target Models are usually small, fast, and fine-tuned to perform a specific task very well (but they don't generalize well beyond the information described in their Dataset). Examples of Target Models are YOLOv8 and DETR.

# %%
%cd {HOME}

from autodistill_yolov8 import YOLOv8

target_model = YOLOv8("yolov8n.pt")
target_model.train(DATA_YAML_PATH, epochs=50)

# %%
!ls {HOME}/runs/detect/train/

# %% [markdown]
# ## ⚖️ Evaluate target model
# 
# **NOTE:** As with the regular YOLOv8 training, we can now take a look at artifacts stored in `runs` directory.

# %%
%cd {HOME}

from IPython.display import Image

Image(filename=f'{HOME}/runs/detect/train/confusion_matrix.png', width=600)

# %%
%cd {HOME}

from IPython.display import Image

Image(filename=f'{HOME}/runs/detect/train/results.png', width=600)

# %%
%cd {HOME}

from IPython.display import Image

Image(filename=f'{HOME}/runs/detect/train/val_batch0_pred.jpg', width=600)

# %% [markdown]
# ## 🎬 Run Inference on a video

# %%
INPUT_VIDEO_PATH = TEST_VIDEO_PATHS[0]
OUTPUT_VIDEO_PATH = f"{HOME}/output.mp4"
TRAINED_MODEL_PATH = f"{HOME}/runs/detect/train/weights/best.pt"

# %%
!yolo predict model={TRAINED_MODEL_PATH} source={INPUT_VIDEO_PATH}

# %% [markdown]
# ## Upload dataset and model to Roboflow

# %% [markdown]
# comming soon...

# %% [markdown]
#   # 🏆 Congratulations
# 
# ### Learning Resources
# 
# Roboflow has produced many resources that you may find interesting as you advance your knowledge of computer vision:
# 
# - [Roboflow Notebooks](https://github.com/roboflow/notebooks): A repository of over 20 notebooks that walk through how to train custom models with a range of model types, from YOLOv7 to SegFormer.
# - [Roboflow YouTube](https://www.youtube.com/c/Roboflow): Our library of videos featuring deep dives into the latest in computer vision, detailed tutorials that accompany our notebooks, and more.
# - [Roboflow Discuss](https://discuss.roboflow.com/): Have a question about how to do something on Roboflow? Ask your question on our discussion forum.
# - [Roboflow Models](https://roboflow.com): Learn about state-of-the-art models and their performance. Find links and tutorials to guide your learning.
# 
# ### Convert data formats
# 
# Roboflow provides free utilities to convert data between dozens of popular computer vision formats. Check out [Roboflow Formats](https://roboflow.com/formats) to find tutorials on how to convert data between formats in a few clicks.
# 
# ### Connect computer vision to your project logic
# 
# [Roboflow Templates](https://roboflow.com/templates) is a public gallery of code snippets that you can use to connect computer vision to your project logic. Code snippets range from sending emails after inference to measuring object distance between detections.


