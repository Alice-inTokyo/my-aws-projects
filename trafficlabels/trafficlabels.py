import boto3
from PIL import Image, ImageDraw, ImageFont
import os
import random
import pandas as pd  # Used to generate Excel files

# List of vehicle types; you can expand it as needed
VEHICLE_TYPES = ['Car', 'Truck', 'Bicycle', 'Bus', 'Motorcycle']

def detect_labels(photo, bucket):
    """
    Use AWS Rekognition to detect labels and object instances in an image.
    :param photo: Image name (in S3)
    :param bucket: S3 bucket name
    :return: List of detected labels
    """
    session = boto3.Session(profile_name='yaoyaoliu')
    client = session.client('rekognition')

    # Call the Rekognition API to detect labels and object instances
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=20  # Increase MaxLabels to detect more labels
    )

    labels = response['Labels']
    return labels

def filter_vehicle_labels(labels):
    """
    Filter out vehicle-type labels.
    :param labels: Label information retrieved from Rekognition
    :return: A dictionary of vehicle types and their instance counts
    """
    vehicle_count = {vehicle: 0 for vehicle in VEHICLE_TYPES}

    for label in labels:
        label_name = label['Name']
        if label_name in VEHICLE_TYPES:
            vehicle_count[label_name] += len(label.get('Instances', []))
    
    return vehicle_count

def draw_vehicle_labels(photo_path, labels, output_dir):
    """
    Draw vehicle labels, bounding boxes, and confidence on the image.
    :param photo_path: Path to the local image
    :param labels: Label information retrieved from Rekognition
    :param output_dir: Directory to save the processed image
    """
    # Open the image
    image = Image.open(photo_path)

    # Convert the image to RGB mode if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    draw = ImageDraw.Draw(image)
    
    # Try loading the font, set the font size larger
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 10)  # Font size set to 40
    except IOError:
        print("Arial font not found, using default font.")
        font = ImageFont.load_default()

    # Loop through all labels and draw relevant information
    for label in labels:
        label_name = label['Name']
        confidence = label['Confidence']

        # If the label belongs to a vehicle type, draw the bounding box
        if label_name in VEHICLE_TYPES:
            for instance in label.get('Instances', []):
                # Get the bounding box
                box = instance['BoundingBox']
                left = image.width * box['Left']
                top = image.height * box['Top']
                width = image.width * box['Width']
                height = image.height * box['Height']

                # Draw a thicker red bounding box
                points = [(left, top), (left + width, top), (left + width, top + height), (left, top + height), (left, top)]
                draw.line(points, fill='#FF0000', width=1)  # Red bounding box, width = 4 pixels

                # Draw the label name and confidence
                text = f"{label_name} ({confidence:.2f}%)"
                draw.text((left, top - 10), text, fill=(255, 0, 0), font=font)  # Red text

    # Create output directory path if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the image to the output folder
    output_image_path = os.path.join(output_dir, f'output_{os.path.basename(photo_path)}')
    image.save(output_image_path)
    print(f"Image saved: {output_image_path}")
    image.show()

def process_images_in_s3_bucket(bucket, output_dir):
    """
    Process all image files in an S3 bucket, perform label detection, and draw bounding boxes.
    :param bucket: S3 bucket name
    :param output_dir: Directory to save processed images
    """
    s3_client = boto3.client('s3')
    
    # List all objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket)
    if 'Contents' not in response:
        print(f"No files found in bucket {bucket}")
        return

    vehicle_totals = {vehicle: 0 for vehicle in VEHICLE_TYPES}  # Initialize vehicle totals
    all_results = []  # Store vehicle statistics for each image

    for obj in response['Contents']:
        photo = obj['Key']
        print(f"Processing file: {photo}")
        
        # Download the image to local storage
        local_photo_path = os.path.join("/tmp", photo)  # Store images in a temporary directory
        s3_client.download_file(bucket, photo, local_photo_path)

        # Detect labels
        labels = detect_labels(photo, bucket)

        # Filter and count vehicle types
        vehicle_count = filter_vehicle_labels(labels)
        all_results.append({'Photo': photo, **vehicle_count})  # Store results in a list
        for vehicle, count in vehicle_count.items():
            vehicle_totals[vehicle] += count

        # Draw labels and confidence scores on the image
        draw_vehicle_labels(local_photo_path, labels, output_dir)

    # Print the vehicle statistics
    print("\nVehicle Statistics:")
    for vehicle, count in vehicle_totals.items():
        print(f"{vehicle}: {count} vehicles")

    # Save the statistics to Excel
    save_vehicle_stats_to_excel(all_results, vehicle_totals, output_dir)

def save_vehicle_stats_to_excel(all_results, vehicle_totals, output_dir):
    """
    Save vehicle statistics to an Excel file and add a total for all vehicles.
    :param all_results: Vehicle statistics for each image
    :param vehicle_totals: Total count of each vehicle type
    :param output_dir: Directory to save the Excel file
    """
    # Save each image's statistics to a DataFrame
    df = pd.DataFrame(all_results)

    # Add a "Total per Type" row to the DataFrame
    total_row = {'Photo': 'Total per Type'}
    total_row.update(vehicle_totals)

    # Use pd.concat to add the row
    total_df = pd.DataFrame([total_row])
    df = pd.concat([df, total_df], ignore_index=True)

    # Calculate the total number of all vehicles
    total_all_vehicles = sum(vehicle_totals.values())
    total_all_row = {'Photo': 'Total Vehicles', 'Total': total_all_vehicles}

    # Add a row that only shows the total for all vehicles
    total_all_df = pd.DataFrame([total_all_row])

    # Use pd.concat again to add the "Total Vehicles" row
    df = pd.concat([df, total_all_df], ignore_index=True)

    # Save the DataFrame as an Excel file
    output_excel_path = os.path.join(output_dir, 'vehicle_stats_with_totals.xlsx')
    df.to_excel(output_excel_path, index=False)  # Save as Excel file
    print(f"Excel file saved: {output_excel_path}")

def main():
    bucket = 'trafficlabels'  # Replace with your S3 bucket name
    output_dir = './processed_results'  # Path for saving the results folder

    # Process all image files in the S3 bucket
    process_images_in_s3_bucket(bucket, output_dir)

if __name__ == "__main__":
    main()