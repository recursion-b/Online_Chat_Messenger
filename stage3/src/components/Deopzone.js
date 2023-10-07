import React, {useCallback} from 'react'
import { Stack } from 'react-bootstrap';
import {useDropzone} from 'react-dropzone'

const dropzoneStyle = {
  width: 100,
  height: 100,
  border: "1px dotted #888"
};
const imageStyle = {
  maxWidth: '100%',
  maxHeight: '100px',
};

function Dropzone({iconImage, setIconImage}) {

  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles)
    const file = acceptedFiles[0];
    console.log(file)
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
      <label>Icon image:</label>
      <div {...getRootProps()} style={dropzoneStyle}>
        <input {...getInputProps()} />
        {
          isDragActive ?
          <p className='mb-0'>Drop the files here ...</p> :
          <p className='mb-0'>Drag 'n' drop some files here, or click to select files</p>
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