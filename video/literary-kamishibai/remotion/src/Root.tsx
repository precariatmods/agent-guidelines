import React from 'react';
import {CalculateMetadataFunction, Composition, staticFile} from 'remotion';
import {KamishibaiVideo, RenderData} from './Video';

type Props = {data: RenderData | null};

const calculateMetadata: CalculateMetadataFunction<Props> = async () => {
  const response = await fetch(staticFile('current/render_data.json'));
  if (!response.ok) {
    throw new Error('render_data.jsonを読み込めません。先にprepare_remotion.pyを実行してください。');
  }
  const data = (await response.json()) as RenderData;
  return {
    durationInFrames: data.total_frames,
    fps: data.fps,
    props: {data},
  };
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Kamishibai"
    component={KamishibaiVideo}
    durationInFrames={30}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{data: null}}
    calculateMetadata={calculateMetadata}
  />
);
