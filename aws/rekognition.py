import boto3
import logging
import json

logger = logging.getLogger(__name__)


class Rekognition():
    client = boto3.client("rekognition")


class Collection(Rekognition):

    collection_id = None

    def __init__(self, collection_id=None):
        self.collection_id = collection_id

    def create_collection(self, collection_id=None):
        collection_id = collection_id or self.collection_id
        response = self.client.create_collection(CollectionId=collection_id)
        if response["StatusCode"] != 200:
            logger.error("Unable to create collection")
            return False
        return response["CollectionArn"]

    def addFaceToCollection(self, bucket, photo_s3_path, collection_id=None):
        # TODO how to add multiple photos for same face?
        collection_id = collection_id or self.collection_id
        logger.info("Adding face %s to collection %s" % (photo_s3_path, collection_id))
        response = self.client.index_faces(CollectionId=collection_id,
                                      Image={"S3Object": {"Bucket": bucket, "Name": photo_s3_path}},
                                      ExternalImageId=photo_s3_path,
                                      MaxFaces=1,
                                      QualityFilter="AUTO",
                                      DetectionAttributes=["ALL"])

        logger.debug("Response '%s'" % json.dumps(response))

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            logger.error("Unable to add face to collection")
            return False
        if not response["FaceRecords"]:
            logger.warning("No faces recorded for %s" % photo_s3_path)
            return False

        if len(response["FaceRecords"]) > 1:
            logger.warning("Multiple faces recorded for %s" % photo_s3_path)
            # use DetectFaces first
            return False

        if len(response["UnindexedFaces"]) > 1:
            logger.warning("Unindexed faces present for %s" % photo_s3_path)
            unindexed = []
            for face in response["UnindexedFaces"]:
                face_id = face["Face"]["FaceId"]
                location = face["Face"]["FaceId"]["BoundingBox"]
                unindexed.append(dict(face_id=face_id, bounding_box=location))
        else:
            unindexed = None

        # We have MaxFaces=1
        face = response["FaceRecords"][0]
        face_id = face["Face"]["FaceId"]
        location = face["Face"]["BoundingBox"]
        logger.info("Added face %s to collection %s" % (photo_s3_path, collection_id))
        return dict(indexed=(dict(face_id=face_id, bounding_box=location)), unindexed=unindexed)

    def search_faces(self, face_id, threshold=80, max_faces=2, collection_id=None):
        collection_id = collection_id or self.collection_id
        response = self.client.search_faces(CollectionId=collection_id,
                                            FaceId=face_id,
                                            FaceMatchThreshold=threshold, # default in aws is > 80
                                            MaxFaces=max_faces)
        if response["StatusCode"] != 200:
            logger.error("Unable to search faces")
            return False
        matches = []
        for match in response["FaceMatches"]:
            face_id = match["Face"]["FaceId"]
            similarity = match["Similarity"] # %
            location = match["Face"]["BoundingBox"]
            matches.append(dict(face_id=face_id, similarity=similarity, bounding_box=location))
        return matches
