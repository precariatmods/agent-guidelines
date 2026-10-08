import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile} from 'remotion';

type RenderLine = {
  line_id: string;
  scene_id: string;
  image: string;
  character: string;
  text: string;
  audio: string;
  start_frame: number;
  audio_frames: number;
  duration_frames: number;
};

export type RenderData = {
  fps: number;
  total_frames: number;
  lines: RenderLine[];
};

type Props = {data: RenderData | null};

const imageStyle: React.CSSProperties = {
  width: '100%',
  height: '100%',
  objectFit: 'cover',
};

export const KamishibaiVideo: React.FC<Props> = ({data}) => {
  if (!data) {
    return <AbsoluteFill style={{backgroundColor: 'black'}} />;
  }

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      {data.lines.map((line) => (
        <Sequence
          key={line.line_id}
          from={line.start_frame}
          durationInFrames={line.duration_frames}
          name={`${line.line_id} ${line.scene_id}`}
        >
          <AbsoluteFill>
            <Img src={staticFile(`current/${line.image}`)} style={imageStyle} />
          </AbsoluteFill>
          <Sequence durationInFrames={line.audio_frames}>
            <Audio src={staticFile(`current/audio/${line.audio}`)} />
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                padding: '0 110px 72px',
                fontFamily: 'sans-serif',
                color: 'white',
              }}
            >
              <div
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.78)',
                  borderRadius: 18,
                  padding: '26px 38px 32px',
                  textShadow: '0 2px 4px black',
                }}
              >
                <div style={{fontSize: 34, marginBottom: 12}}>{line.character}</div>
                <div style={{fontSize: 52, lineHeight: 1.45}}>{line.text}</div>
              </div>
            </AbsoluteFill>
          </Sequence>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
