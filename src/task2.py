import numpy as np
import matplotlib.pyplot as plt
import json
import copy
import os
from task2_tools import read_predicted_boxes, read_ground_truth_boxes

def calculate_iou(prediction_box, gt_box):
    #TASK 2a
    xmin, ymin, xmax, ymax = 0,1,2,3
    """Calculate intersection over union of single predicted and ground truth box.

    Args:
        prediction_box (np.array of floats): location of predicted object as
            [xmin, ymin, xmax, ymax]
        gt_box (np.array of floats): location of ground truth object as
            [xmin, ymin, xmax, ymax]

        returns:
            float: value of the intersection of union for the two boxes.
    """
    
    dx = min(prediction_box[xmax], gt_box[xmax]) - max(prediction_box[xmin], gt_box[xmin])
    dy = min(prediction_box[ymax], gt_box[ymax]) - max(prediction_box[ymin], gt_box[ymin])

    if (dx>0) and (dy>0): 
        intersection = float(dx*dy)
    else: 
        intersection = 0
    
    area_prediction_box = (prediction_box[xmax]-prediction_box[xmin])*(prediction_box[ymax]-prediction_box[ymin])
    area_gt_box = (gt_box[xmax]-gt_box[xmin])*(gt_box[ymax]-gt_box[ymin])

    union = float(area_prediction_box + area_gt_box - intersection)

    iou = intersection/union

    return iou

def calculate_precision(num_tp, num_fp, num_fn):
    #TASK 2b
    #UNUSED ARGUMENT: num_fn
    """ Calculates the precision for the given parameters.
        Returns 1 if num_tp + num_fp = 0

    Args:
        num_tp (float): number of true positives
        num_fp (float): number of false positives
        num_fn (float): number of false negatives
    Returns:
        float: value of precision
    """
    if (num_tp + num_fp) == 0:
        return 1

    return num_tp / float(num_tp + num_fp)


def calculate_recall(num_tp, num_fp, num_fn):
    #TASK 2b
    #UNUSED ARGUMENT: num_fp
    """ Calculates the recall for the given parameters.
        Returns 0 if num_tp + num_fn = 0
    Args:
        num_tp (float): number of true positives
        num_fp (float): number of false positives
        num_fn (float): number of false negatives
    Returns:
        float: value of recall
    """
    if (num_tp + num_fn) == 0:
        return 0

    return num_tp / float(num_tp + num_fn)


def get_all_box_matches(prediction_boxes, gt_boxes, iou_threshold):
    """Finds all possible matches for the predicted boxes to the ground truth boxes.
        No bounding box can have more than one match.

        Remember: Matching of bounding boxes should be done with decreasing IoU order!

    Args:
        prediction_boxes: (np.array of floats): list of predicted bounding boxes
            shape: [number of predicted boxes, 4].
            Each row includes [xmin, ymin, xmax, ymax]
        gt_boxes: (np.array of floats): list of bounding boxes ground truth
            objects with shape: [number of ground truth boxes, 4].
            Each row includes [xmin, ymin, xmax, ymax]
    Returns the matched boxes (in corresponding order):
        prediction_boxes: (np.array of floats): list of predicted bounding boxes
            shape: [number of box matches, 4].
        gt_boxes: (np.array of floats): list of bounding boxes ground truth
            objects with shape: [number of box matches, 4].
            Each row includes [xmin, ymin, xmax, ymax]
    """
    num_prediction_boxes = prediction_boxes.shape[0]
    num_gt_boxes = gt_boxes.shape[0]
    
    ########### Find all possible matches with a IoU >= iou threshold
    all_box_matches = []
    for pb_idx in range(num_prediction_boxes):
        for gt_idx in range(num_gt_boxes):
            iou = calculate_iou(prediction_boxes[pb_idx], gt_boxes[gt_idx])
            if iou >= iou_threshold:
                all_box_matches.append(tuple((pb_idx, gt_idx, iou)))
    
    if not all_box_matches:
        return np.array([]), np.array([])

    ########### Sort all matches on IoU in descending order
     
    dtype = [('prediction box index', int), ('ground truth index', int), ('iou', float)]
    all_box_matches = np.array(all_box_matches, dtype=dtype)
    all_box_matches = np.sort(all_box_matches, order='iou')
    all_box_matches = np.flip(all_box_matches, axis=0)
    num_matches = all_box_matches.shape[0]

    ########### Find all matches with the highest IoU threshold
    best_box_matches = [all_box_matches[0]]
    for match_idx in range(1, num_matches):
        exists_better_match = False
        
        for best_idx in range(len(best_box_matches)):
            if (all_box_matches[match_idx][0] == best_box_matches[best_idx][0]) or (all_box_matches[match_idx][1] == best_box_matches[best_idx][1]):
                exists_better_match = True
                break

        if not exists_better_match:
            best_box_matches.append(all_box_matches[match_idx])
    
    num_matches = len(best_box_matches)

    prediction_matches = np.zeros([num_matches,4])
    gt_matches = np.zeros([num_matches,4])

    for match in range(num_matches):
        pb_idx = best_box_matches[match][0]
        gt_idx = best_box_matches[match][1]

        prediction_matches[match] = prediction_boxes[pb_idx]
        gt_matches[match] = gt_boxes[gt_idx]

    return prediction_matches, gt_matches



def calculate_individual_image_result(
        prediction_boxes, gt_boxes, iou_threshold):
    """Given a set of prediction boxes and ground truth boxes,
       calculates true positives, false positives and false negatives
       for a single image.
       NB: prediction_boxes and gt_boxes are not matched!

    Args:
        prediction_boxes: (np.array of floats): list of predicted bounding boxes
            shape: [number of predicted boxes, 4].
            Each row includes [xmin, ymin, xmax, ymax]
        gt_boxes: (np.array of floats): list of bounding boxes ground truth
            objects with shape: [number of ground truth boxes, 4].
            Each row includes [xmin, ymin, xmax, ymax]
    Returns:
        dict: containing true positives, false positives, true negatives, false negatives
            {"true_pos": int, "false_pos": int, "false_neg": int}
    """

    # Find the bounding box matches with the highest IoU threshold
    prediction_matches, gt_matches = get_all_box_matches(prediction_boxes, gt_boxes, iou_threshold)

    num_prediction_boxes = prediction_boxes.shape[0]
    num_gt_boxes = gt_boxes.shape[0]
    num_matches = prediction_matches.shape[0]

    # Compute true positives, false positives, false negatives
    true_positives = num_matches
    false_positives = num_prediction_boxes - num_matches
    false_negatives = num_gt_boxes - num_matches

    results = {"true_pos": true_positives, "false_pos": false_positives, "false_neg": false_negatives}

    return results



def calculate_precision_recall_all_images(
        all_prediction_boxes, all_gt_boxes, iou_threshold):
    """Given a set of prediction boxes and ground truth boxes for all images,
       calculates recall and precision over all images.

       NB: all_prediction_boxes and all_gt_boxes are not matched!

    Args:
        all_prediction_boxes: (list of np.array of floats): each element in the list
            is a np.array containing all predicted bounding boxes for the given image
            with shape: [number of predicted boxes, 4].
            Each row includes [xmin, xmax, ymin, ymax]
        all_gt_boxes: (list of np.array of floats): each element in the list
            is a np.array containing all ground truth bounding boxes for the given image
            objects with shape: [number of ground truth boxes, 4].
            Each row includes [xmin, xmax, ymin, ymax]
    Returns:
        tuple: (precision, recall). Both float.
    """
    # Find total true positives, false positives and false negatives over all images
    num_images = len(all_prediction_boxes)

    tot_true_positives = 0
    tot_false_positives = 0
    tot_false_negatives = 0

    for image in range(num_images):
        image_result = calculate_individual_image_result(all_prediction_boxes[image], all_gt_boxes[image], iou_threshold)
        
        tot_true_positives += image_result["true_pos"]
        tot_false_positives += image_result["false_pos"]
        tot_false_negatives += image_result["false_neg"]

    # Compute precision, recall
    precision = calculate_precision(tot_true_positives, tot_false_positives, tot_false_negatives)
    recall = calculate_recall(tot_true_positives, tot_false_positives, tot_false_negatives)
    
    return precision, recall


def get_precision_recall_curve(all_prediction_boxes, all_gt_boxes,
                               confidence_scores, iou_threshold):
    """Given a set of prediction boxes and ground truth boxes for all images,
       calculates the recall-precision curve over all images. Use the given
       confidence thresholds to find the precision-recall curve.

       NB: all_prediction_boxes and all_gt_boxes are not matched!

    Args:
        all_prediction_boxes: (list of np.array of floats): each element in the list
            is a np.array containing all predicted bounding boxes for the given image
            with shape: [number of predicted boxes, 4].
            Each row includes [xmin, xmax, ymin, ymax]
        all_gt_boxes: (list of np.array of floats): each element in the list
            is a np.array containing all ground truth bounding boxes for the given image
            objects with shape: [number of ground truth boxes, 4].
            Each row includes [xmin, xmax, ymin, ymax]
        scores: (list of np.array of floats): each element in the list
            is a np.array containting the confidence score for each of the
            predicted bounding box. Shape: [number of predicted boxes]

            E.g: score[0][1] is the confidence score for a predicted bounding box 1 in image 0.
    Returns:
        tuple: (precision, recall). Both np.array of floats.
    """
    # Instead of going over every possible confidence score threshold to compute the PR 
    # curve, we will use an approximation
    # DO NOT CHANGE. If you change this, the tests will not pass when we run the final evaluation
    num_thresholds = 500
    confidence_thresholds = np.linspace(0, 1, num_thresholds)

    # YOUR CODE HERE

    precisions = np.zeros([num_thresholds,])
    recalls = np.zeros([num_thresholds,])

    
    for t in range(num_thresholds):
        all_predictions_over_threshold = []

        for image in range(len(confidence_scores)):
            image_boxes = confidence_scores[image]
            image_predictions_over_threshold = []

            for box in range(image_boxes.shape[0]):

                if confidence_scores[image][box] >= confidence_thresholds[t]:
                    image_predictions_over_threshold.append(all_prediction_boxes[image][box])

            image_predictions_over_threshold = np.array(image_predictions_over_threshold)
            all_predictions_over_threshold.append(image_predictions_over_threshold)

        precisions[t] , recalls[t] = calculate_precision_recall_all_images(all_predictions_over_threshold,all_gt_boxes,iou_threshold)


    return precisions, recalls



def plot_precision_recall_curve(precisions, recalls):
    """Plots the precision recall curve.
        Save the figure to precision_recall_curve.png:
        'plt.savefig("precision_recall_curve.png")'

    Args:
        precisions: (np.array of floats) length of N
        recalls: (np.array of floats) length of N
    Returns:
        None
    """
    # No need to edit this code.
    plt.figure(figsize=(20, 20))
    plt.plot(recalls, precisions)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.xlim([0.8, 1.0])
    plt.ylim([0.8, 1.0])
    os.makedirs("../docs", exist_ok=True)
    plt.savefig(os.path.join("../docs", "precision_recall_curve.png"))


def calculate_mean_average_precision(precisions, recalls):
    """ Given a precision recall curve, calculates the mean average
        precision.

    Args:
        precisions: (np.array of floats) length of N
        recalls: (np.array of floats) length of N
    Returns:
        float: mean average precision
    """
    # Calculate the mean average precision given these recall levels.
    # DO NOT CHANGE. If you change this, the tests will not pass when we run the final
    # evaluation
    num_recall_levels = 11
    recall_levels = np.linspace(0, 1.0, num_recall_levels)
    # YOUR CODE HERE

    N = recalls.shape[0]
    
    sum_max_precisions = 0
    for level in range(num_recall_levels):
        max_precision = 0
        for n in range(N):
            if (recalls[n] >= recall_levels[level]) and (precisions[n]>max_precision):
                max_precision = precisions[n]
        sum_max_precisions += max_precision
        
    average_precisions = sum_max_precisions / (float(num_recall_levels))

    return average_precisions




def mean_average_precision(ground_truth_boxes, predicted_boxes):
    """ Calculates the mean average precision over the given dataset
        with IoU threshold of 0.5

    Args:
        ground_truth_boxes: (dict)
        {
            "img_id1": (np.array of float). Shape [number of GT boxes, 4]
        }
        predicted_boxes: (dict)
        {
            "img_id1": {
                "boxes": (np.array of float). Shape: [number of pred boxes, 4],
                "scores": (np.array of float). Shape: [number of pred boxes]
            }
        }
    """
    # DO NOT EDIT THIS CODE
    all_gt_boxes = []
    all_prediction_boxes = []
    confidence_scores = []

    for image_id in ground_truth_boxes.keys():
        pred_boxes = predicted_boxes[image_id]["boxes"]
        scores = predicted_boxes[image_id]["scores"]

        all_gt_boxes.append(ground_truth_boxes[image_id])
        all_prediction_boxes.append(pred_boxes)
        confidence_scores.append(scores)
    iou_threshold = 0.5
    precisions, recalls = get_precision_recall_curve(all_prediction_boxes,
                                                     all_gt_boxes,
                                                     confidence_scores,
                                                     iou_threshold)
    plot_precision_recall_curve(precisions, recalls)
    mean_average_precision = calculate_mean_average_precision(precisions, recalls)
    print("Mean average precision: {:.4f}".format(mean_average_precision))


if __name__ == "__main__":
    ground_truth_boxes = read_ground_truth_boxes()
    predicted_boxes = read_predicted_boxes()
    mean_average_precision(ground_truth_boxes, predicted_boxes)
