# Augmented Reality (ARPAS)

## Data Structure

Variant → ARObject → Scene → (Item (Topic) → Module → Project) # () is not part of th ar app )

## Frontend Connection

The augmented reality React is loaded through the React widget `react_augmentedreality_arc`.
The AR widget is displayed on topic detail pages at: `/{organisation_slug}/topicprio/{year}-{pk}/`
Example: `/berlin/topicprio/2024-123/`


### Provided Data

The widget provides the following data for the topic: #example values
{ 
    "content_types": {
        "variant_content_type_id": ContentType.objects.get_for_model(Variant).id,
        "comments_content_type_id": ContentType.objects.get_for_model(Comment).id,
    },
    "topic": {
        "id": topic.id,
        "slug": topic.slug,
        "name": topic.name,
        "description": topic.description,
        "category": topic.category.name,
        "labels": [label.name for label in topic.labels.all()],
        "module": topic.module.name,
        "created": topic.created,
    },
    "scene": {
        "id": scene.id,
        "object_id": scene.object_id,
        "content_type": scene.content_type.id,
        "objects": [
            {
                "id": ar_object.id,
                "name": ar_object.name,
                "qr_id": ar_object.qr_id,
                "coordinates": [lat, lng, alt],
                "variants": [
                    {
                        "id": variant.id,
                        "name": variant.name,
                        "mesh_id": variant.mesh_id,
                        "mesh_url": presigned_url,
                        "offset_position": [x, y, z],
                        # ... all Variant-Data
                    }
                ]
            }
        ]
}
}

The content types ids are important for the call to the API

### API Endpoints

- **Ratings**: `/api/contenttypes/{content_type}/objects/{object_pk}/arpas-ratings/`
- **Comments**: `/api/contenttypes/{content_type}/objects/{object_pk}/arpas-comments/`

The Endpoint provide Comments (or ratings) for various content_types. By now for Example Ratings for Variants and Comments
To use the Endpoint you need for Exmaple the comments_content_type_id (as {content_type}) and the comments.id (as {object_pk}) to update the rating for that given comments object.  
    

### API Documentation

View the complete API documentation at `/api/docs/` for detailed endpoint information and request/response schemas.
