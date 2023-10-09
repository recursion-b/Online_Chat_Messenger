import React, {useCallback} from 'react'
import { Stack } from 'react-bootstrap';
import {useDropzone} from 'react-dropzone'

const dropzoneStyle = {
  width: 120,
  height: 40,
  border: "1px solid #888",
  borderRadius: "4px",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  cursor: "pointer"
};
const imageStyle = {
  maxWidth: '70%',
  maxHeight: '80px',
};

function Dropzone({iconImage, setIconImage}) {

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0];
    if (file !== undefined) {
      const reader = new FileReader();
  
      reader.onload = () => {
        setIconImage(reader.result)
        console.log(reader.result)
      };
  
      reader.readAsDataURL(file)
    }
  }, [setIconImage])

  const {getRootProps, getInputProps, isDragActive} = useDropzone({
    accept: {
      'image/png': [],
      'image/jpeg': []},
      maxFiles:1,
      multiple: false,
      onDrop
    })

  return (
    <Stack direction='horizontal' gap={3}>
      <label>Your icon:</label>
      <div {...getRootProps()} style={dropzoneStyle}>
        <input {...getInputProps()} />
        {
          isDragActive ?
          <div>Drop Image</div> :
          <div>Upload Image</div>
        }
      </div>
      {iconImage && (
        <div>
          <img src={iconImage} alt='user-icon' style={imageStyle} />
        </div>
      )}
    </Stack>
  )
}

export default Dropzone;