import React, { useState, useRef } from 'react';
import { Upload, X, ImageOff } from 'lucide-react';

interface ImageUploadProps {
  currentImageUrl?: string | null;
  onImageSelect: (file: File | null) => void;
  onImageDelete?: () => void;
  disabled?: boolean;
  error?: string;
  onError?: (message: string) => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  currentImageUrl,
  onImageSelect,
  onImageDelete,
  disabled = false,
  error,
  onError,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentImageUrl || null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    if (!file) {
      setPreviewUrl(null);
      onImageSelect(null);
      return;
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      const errorMsg = 'Please select an image file (jpg, png, webp)';
      if (onError) {
        onError(errorMsg);
      } else {
        alert(errorMsg);
      }
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      const errorMsg = 'Image size must be less than 5MB';
      if (onError) {
        onError(errorMsg);
      } else {
        alert(errorMsg);
      }
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
    };
    reader.readAsDataURL(file);

    onImageSelect(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileChange(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreviewUrl(null);
    onImageSelect(null);
    if (onImageDelete) {
      onImageDelete();
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative aspect-video w-full cursor-pointer overflow-hidden rounded-lg border-2 border-dashed transition-all ${
          isDragging
            ? 'border-primary bg-primary/5'
            : error
            ? 'border-error bg-error/5'
            : 'border-gray-300 bg-gray-50 hover:border-primary hover:bg-primary/5'
        } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
      >
        {previewUrl ? (
          <>
            <img
              src={previewUrl}
              alt="Preview"
              className="h-full w-full object-cover"
            />
            {!disabled && (
              <button
                onClick={handleDelete}
                className="absolute right-2 top-2 rounded-full bg-error p-2 text-white shadow-lg transition-transform hover:scale-110"
                aria-label="Remove image"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </>
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center p-6 text-center">
            {isDragging ? (
              <>
                <Upload className="mb-2 h-12 w-12 text-primary" />
                <p className="text-sm font-medium text-primary">Drop image here</p>
              </>
            ) : (
              <>
                <ImageOff className="mb-2 h-12 w-12 text-gray-400" />
                <p className="mb-1 text-sm font-medium text-gray-700">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  JPG, PNG, WEBP (max 5MB)
                </p>
              </>
            )}
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
        className="hidden"
        disabled={disabled}
      />
    </div>
  );
};

